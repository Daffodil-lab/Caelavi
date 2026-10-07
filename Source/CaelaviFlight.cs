using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace Caelavi;

public sealed class CompProperties_CaelaviFlight : CompProperties
{
    public CompProperties_CaelaviFlight()
    {
        compClass = typeof(CompCaelaviFlight);
    }
}

/// <summary>Manual, persistent wing deployment for a Caelavi pawn.</summary>
public sealed class CompCaelaviFlight : ThingComp
{
    private const float FlightMinimumAgeYears = 13f;
    private const string WingDefName = "CA_Wing";
    private const string WingGroupDefName = "CA_Wings";
    private const string FlightHediffDefName = "CA_DeployedFlight";
    private bool deployed;

    private Pawn Pawn => (Pawn)parent;

    /// <summary>The player's stored wing position, including while buffs are suppressed.</summary>
    public bool Deployed => deployed;

    /// <summary>One or two usable wings while deployment is currently effective.</summary>
    public int EffectiveWingCount
    {
        get
        {
            Pawn pawn = Pawn;
            if (!deployed || pawn.ageTracker == null ||
                pawn.ageTracker.AgeBiologicalYearsFloat < FlightMinimumAgeYears ||
                pawn.health?.hediffSet == null || WingsProtected(pawn))
            {
                return 0;
            }
            return AvailableWingCount(pawn);
        }
    }

    private bool CanDeploy => Pawn.ageTracker != null &&
                              Pawn.ageTracker.AgeBiologicalYearsFloat >= FlightMinimumAgeYears &&
                              AvailableWingCount(Pawn) > 0;

    public override void PostExposeData()
    {
        Scribe_Values.Look(ref deployed, "caelaviWingsDeployed", defaultValue: false);
    }

    public override void PostSpawnSetup(bool respawningAfterLoad)
    {
        base.PostSpawnSetup(respawningAfterLoad);
        Synchronize();
    }

    public override void CompTickInterval(int delta)
    {
        // A wing injury, apparel change, or 13th birthday takes effect on the
        // next pawn tick. There is no time limit or automatic retraction.
        Synchronize();
    }

    public override IEnumerable<Gizmo> CompGetGizmosExtra()
    {
        if (Pawn.Faction != Faction.OfPlayer)
        {
            yield break;
        }

        var command = new Command_Toggle
        {
            defaultLabel = "CA_Flight_ToggleLabel".Translate(),
            defaultDesc = "CA_Flight_ToggleDescription".Translate(),
            icon = TexCommand.HoldOpen,
            isActive = () => deployed,
            toggleAction = () =>
            {
                if (deployed || CanDeploy)
                {
                    deployed = !deployed;
                    Synchronize();
                }
            }
        };
        if (!deployed && !CanDeploy)
        {
            command.Disable("CA_Flight_RequiresAgeAndWing".Translate());
        }
        yield return command;
    }

    /// <summary>Align the vanilla Hediff and its stage with the live wing state.</summary>
    public void Synchronize()
    {
        Pawn pawn = Pawn;
        if (pawn.health?.hediffSet == null)
        {
            return;
        }
        HediffDef flightDef = DefDatabase<HediffDef>.GetNamedSilentFail(FlightHediffDefName);
        if (flightDef == null)
        {
            return;
        }
        Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(flightDef);
        int wingCount = EffectiveWingCount;
        if (wingCount == 0)
        {
            if (existing != null)
            {
                pawn.health.RemoveHediff(existing);
            }
            return;
        }
        if (existing == null)
        {
            existing = pawn.health.AddHediff(flightDef);
        }
        if (existing.Severity != wingCount)
        {
            existing.Severity = wingCount;
        }
    }

    private static int AvailableWingCount(Pawn pawn)
    {
        if (pawn.RaceProps.body == null || pawn.health?.hediffSet == null)
        {
            return 0;
        }
        int count = 0;
        foreach (BodyPartRecord part in pawn.RaceProps.body.AllParts)
        {
            if (part.def.defName == WingDefName && !pawn.health.hediffSet.PartIsMissing(part))
            {
                count++;
            }
        }
        return Math.Min(count, 2);
    }

    private static bool WingsProtected(Pawn pawn)
    {
        BodyPartGroupDef wingGroup = DefDatabase<BodyPartGroupDef>.GetNamedSilentFail(WingGroupDefName);
        if (wingGroup == null)
        {
            // A broken wing-group Def must not silently grant flight through
            // protective gear whose coverage cannot be checked.
            return true;
        }
        if (pawn.apparel == null)
        {
            return false;
        }
        foreach (Apparel apparel in pawn.apparel.WornApparel)
        {
            if (apparel.def.apparel?.CoversBodyPartGroup(wingGroup) == true)
            {
                return true;
            }
        }
        return false;
    }
}

// Pawn components load before Pawn's health and apparel fields. Reconcile only
// after the complete Pawn has finished its PostLoadInit pass.
[HarmonyPatch(typeof(Pawn), nameof(Pawn.ExposeData))]
internal static class CaelaviFlightLoadPatch
{
    private static void Postfix(Pawn __instance)
    {
        if (Scribe.mode == LoadSaveMode.PostLoadInit)
        {
            __instance.GetComp<CompCaelaviFlight>()?.Synchronize();
        }
    }
}

// VEF Floating removes path cost outright. A narrow postfix preserves normal
// passability and reduces only the terrain's actual contribution to move cost.
[HarmonyPatch(typeof(Pawn_PathFollower), "CostToMoveIntoCell",
    new[] { typeof(Pawn), typeof(IntVec3) })]
[HarmonyPriority(Priority.Last)]
internal static class CaelaviTerrainCostPatch
{
    private static void Postfix(Pawn pawn, IntVec3 c, ref float __result)
    {
        int wings = pawn.GetComp<CompCaelaviFlight>()?.EffectiveWingCount ?? 0;
        if (wings == 0 || pawn.Map == null || !c.InBounds(pawn.Map))
        {
            return;
        }
        TerrainDef terrain = c.GetTerrain(pawn.Map);
        if (terrain == null || terrain.pathCost <= 0 ||
            terrain.passability == Traversability.Impassable ||
            Pawn_PathFollower.GetPawnCellBaseCostOverride(pawn, c).HasValue)
        {
            return;
        }
        // Another VEF effect has already removed this cost; do not discount it
        // again. Caelavi's own flight does not register as VEF Floating.
        if (VEF.AnimalBehaviours.StaticCollectionsClass.floating_animals?.Contains(pawn) == true ||
            (terrain.IsWater && VEF.AnimalBehaviours.StaticCollectionsClass.waterstriding_pawns?.Contains(pawn) == true))
        {
            return;
        }

        PathGrid grid = pawn.Map.pathing.For(pawn).pathGrid;
        int withTerrain = grid.CalculatedCostAt(c, perceivedStatic: false, pawn.Position);
        int withoutTerrain = grid.CalculatedCostAt(c, perceivedStatic: false, pawn.Position, baseCostOverride: 0);
        int terrainContribution = withTerrain - withoutTerrain;
        if (withTerrain >= 10000 || terrainContribution <= 0)
        {
            return;
        }

        float reduction = wings == 2 ? 0.60f : 0.30f;
        float urgencyFactor = 1f;
        if (pawn.CurJob != null)
        {
            urgencyFactor = pawn.CurJob.locomotionUrgency switch
            {
                LocomotionUrgency.Amble => 3f,
                LocomotionUrgency.Walk => 2f,
                LocomotionUrgency.Sprint => 0.75f,
                _ => 1f
            };
        }
        __result = Mathf.Max(1f, __result - terrainContribution * reduction * urgencyFactor);
    }
}
