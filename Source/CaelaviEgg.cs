using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace Caelavi;

/// <summary>
/// A single Caelavi child. Keeping one embryo per Thing prevents parents and
/// inherited genes from being combined when eggs are hauled or stored.
/// </summary>
public sealed class CompProperties_CaelaviEgg : CompProperties
{
    public float daysToHatch = 12f;

    public CompProperties_CaelaviEgg()
    {
        compClass = typeof(CompCaelaviEgg);
    }
}

public sealed class CompCaelaviEgg : ThingComp
{
    private const string ChildKindDefName = "CA_DevelopmentPawn";
    private const int TicksPerDay = 60000;
    private static bool missingKindReported;

    private Pawn? mother;
    private Pawn? father;
    private Faction? faction;
    private GeneSet? inheritedGenes;
    private int incubationTicks;
    private bool initialized;

    private CompProperties_CaelaviEgg Props => (CompProperties_CaelaviEgg)props;

    public void Initialize(Pawn eggMother, Pawn? eggFather, Faction? eggFaction, GeneSet? genes)
    {
        mother = eggMother;
        father = eggFather;
        faction = eggFaction;
        inheritedGenes = genes?.Copy();
        incubationTicks = 0;
        initialized = true;

        // This vanilla comp keeps world pawns referenced by an item alive
        // through travel, death and save/load until the egg is destroyed.
        CompHasPawnSources? sources = parent.TryGetComp<CompHasPawnSources>();
        sources?.AddSource(mother);
        if (father != null && father != mother)
        {
            sources?.AddSource(father);
        }
    }

    public override void PostExposeData()
    {
        base.PostExposeData();
        Scribe_References.Look(ref mother, "mother");
        Scribe_References.Look(ref father, "father");
        Scribe_References.Look(ref faction, "faction");
        Scribe_Deep.Look(ref inheritedGenes, "inheritedGenes");
        Scribe_Values.Look(ref incubationTicks, "incubationTicks", 0);
        Scribe_Values.Look(ref initialized, "initialized", false);
    }

    public override void CompTick()
    {
        base.CompTick();
        if (!initialized || parent.Destroyed || parent.TryGetComp<CompTemperatureRuinable>()?.Ruined == true)
        {
            return;
        }

        int requiredTicks = Math.Max(1, (int)(Props.daysToHatch * TicksPerDay));
        if (incubationTicks < requiredTicks)
        {
            incubationTicks++;
        }
        if (incubationTicks >= requiredTicks)
        {
            Hatch();
        }
    }

    public override string CompInspectStringExtra()
    {
        if (!initialized || parent.TryGetComp<CompTemperatureRuinable>()?.Ruined == true)
        {
            return string.Empty;
        }
        int requiredTicks = Math.Max(1, (int)(Props.daysToHatch * TicksPerDay));
        int percent = Math.Min(100, incubationTicks * 100 / requiredTicks);
        return "CA_EggHatchProgress".Translate(percent);
    }

    private void Hatch()
    {
        PawnKindDef childKind = DefDatabase<PawnKindDef>.GetNamedSilentFail(ChildKindDefName);
        if (childKind == null)
        {
            if (!missingKindReported)
            {
                missingKindReported = true;
                Log.Error("[Caelavi] Missing child PawnKindDef CA_DevelopmentPawn; egg cannot hatch.");
            }
            return;
        }

        // In the alpha, age three is both the biological and displayed age.
        // Generate at this age so child stories and life-stage data are made
        // for a child, rather than ageing down an already generated adult.
        var genes = inheritedGenes == null
            ? new List<GeneDef>()
            : new List<GeneDef>(inheritedGenes.GenesListForReading);
        var request = new PawnGenerationRequest(
            kind: childKind,
            faction: faction,
            context: PawnGenerationContext.NonPlayer,
            forceGenerateNewPawn: true,
            canGeneratePawnRelations: false,
            allowPregnant: false,
            fixedBiologicalAge: 3f,
            fixedChronologicalAge: 3f,
            forcedEndogenes: genes,
            developmentalStages: DevelopmentalStage.Child,
            forceNoGear: true);
        Pawn child = PawnGenerator.GeneratePawn(request);
        if (!PawnUtility.TrySpawnHatchedOrBornPawn(child, parent))
        {
            child.Destroy(DestroyMode.Vanish);
            return;
        }

        if (mother != null && !child.relations.DirectRelationExists(PawnRelationDefOf.Parent, mother))
        {
            child.relations.AddDirectRelation(PawnRelationDefOf.Parent, mother);
        }
        if (father != null && father != mother && !child.relations.DirectRelationExists(PawnRelationDefOf.Parent, father))
        {
            child.relations.AddDirectRelation(PawnRelationDefOf.Parent, father);
        }
        parent.Destroy(DestroyMode.Vanish);
    }
}

/// <summary>
/// Vanilla Lovin and pregnancy still decide whether conception happens and
/// record the father and inherited GeneSet. At six days we replace labor with
/// one to three separate eggs only when the pregnant pawn is Caelavi.
/// </summary>
[HarmonyPatch(typeof(Hediff_Pregnant), nameof(Hediff_Pregnant.StartLabor))]
internal static class CaelaviEggStartLaborPatch
{
    private const string RaceDefName = "CA_Caelavi";
    private const string EggDefName = "CA_FertilizedEgg";

    private static bool Prefix(Hediff_Pregnant __instance)
    {
        Pawn mother = __instance.pawn;
        if (mother?.def?.defName != RaceDefName)
        {
            return true;
        }

        ThingDef eggDef = DefDatabase<ThingDef>.GetNamedSilentFail(EggDefName);
        if (eggDef == null)
        {
            Log.Error("[Caelavi] Missing CA_FertilizedEgg; using vanilla labor to avoid losing a pregnancy.");
            return true;
        }

        // Trial distribution only: each clutch size has the same chance.
        int eggCount = Rand.RangeInclusive(1, 3);
        int placedCount = 0;
        Pawn? father = __instance.Father;
        GeneSet? originalGenes = __instance.geneSet;

        for (int index = 0; index < eggCount; index++)
        {
            ThingWithComps? egg = ThingMaker.MakeThing(eggDef) as ThingWithComps;
            if (egg == null)
            {
                Log.Error("[Caelavi] CA_FertilizedEgg is not a ThingWithComps.");
                break;
            }
            CompCaelaviEgg? embryo = egg.TryGetComp<CompCaelaviEgg>();
            if (embryo == null)
            {
                Log.Error("[Caelavi] CA_FertilizedEgg has no CompCaelaviEgg.");
                egg.Destroy(DestroyMode.Vanish);
                break;
            }

            GeneSet? genes = originalGenes;
            if (index > 0 && father != null)
            {
                GeneSet rolledGenes = PregnancyUtility.GetInheritedGeneSet(father, mother, out bool success);
                if (success && rolledGenes != null)
                {
                    genes = rolledGenes;
                }
            }

            embryo.Initialize(mother, father, mother.Faction, genes);
            if (PlaceEgg(mother, egg))
            {
                placedCount++;
            }
            else
            {
                egg.Destroy(DestroyMode.Vanish);
                Log.Error("[Caelavi] Could not place a Caelavi egg beside or in its mother.");
            }
        }

        // If no egg could be placed, keep vanilla childbirth as a fail-safe.
        // The normal path skips labor; TickInterval then removes pregnancy.
        if (placedCount == 0)
        {
            return true;
        }
        if (placedCount != eggCount)
        {
            Log.Warning($"[Caelavi] Laid {placedCount} of {eggCount} selected eggs for {mother}.");
        }
        return false;
    }

    private static bool PlaceEgg(Pawn mother, Thing egg)
    {
        Map map = mother.MapHeld;
        if (map != null && GenPlace.TryPlaceThing(egg, mother.PositionHeld, map, ThingPlaceMode.Near))
        {
            return true;
        }
        return mother.inventory?.innerContainer.TryAdd(egg, canMergeWithExistingStacks: false) == true;
    }
}
