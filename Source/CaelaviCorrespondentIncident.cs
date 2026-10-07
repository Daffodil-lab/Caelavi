using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Caelavi;

/// <summary>
/// Storyteller incident independent of scenario parts and quest scripts. The
/// offer is a saved choice letter; the pawn is generated only on acceptance.
/// </summary>
public sealed class IncidentWorker_CaelaviCorrespondentJoin : IncidentWorker
{
    private const string OfferLetterDefName = "CA_CorrespondentOffer";

    protected override bool CanFireNowSub(IncidentParms parms)
    {
        return parms.target is Map map
            && map.IsPlayerHome
            && Faction.OfPlayer != null
            && def.pawnKind != null
            && RCellFinder.TryFindRandomPawnEntryCell(
                out _, map, CellFinder.EdgeRoadChance_Friendly);
    }

    protected override bool TryExecuteWorker(IncidentParms parms)
    {
        if (!(parms.target is Map map) || !map.IsPlayerHome ||
            def.pawnKind == null || Faction.OfPlayer == null ||
            !RCellFinder.TryFindRandomPawnEntryCell(
                out _, map, CellFinder.EdgeRoadChance_Friendly))
        {
            return false;
        }

        LetterDef offerDef = DefDatabase<LetterDef>.GetNamedSilentFail(OfferLetterDefName);
        if (offerDef == null)
        {
            Log.Error("[Caelavi] Missing CA_CorrespondentOffer LetterDef.");
            return false;
        }

        var offer = LetterMaker.MakeLetter(def.letterLabel, def.letterText, offerDef)
            as ChoiceLetter_CaelaviCorrespondent;
        if (offer == null)
        {
            Log.Error("[Caelavi] CA_CorrespondentOffer has no Caelavi choice-letter class.");
            return false;
        }

        offer.targetMap = map;
        offer.pawnKindDefName = def.pawnKind.defName;
        Find.LetterStack.ReceiveLetter(offer);
        return true;
    }
}

/// <summary>
/// The letter stack saves this offer and its target map across game reloads.
/// No pawn or faction membership is created while the offer is pending.
/// </summary>
public sealed class ChoiceLetter_CaelaviCorrespondent : ChoiceLetter
{
    public Map? targetMap;
    public string pawnKindDefName = "CA_DevelopmentPawn";

    public override bool CanDismissWithRightClick => false;

    public override IEnumerable<DiaOption> Choices
    {
        get
        {
            if (targetMap?.IsPlayerHome == true)
            {
                yield return new DiaOption("CA_CorrespondentAccept".Translate())
                {
                    action = () =>
                    {
                        if (TryAccept())
                        {
                            Find.LetterStack.RemoveLetter(this);
                        }
                    }
                };
            }

            yield return new DiaOption("CA_CorrespondentDecline".Translate())
            {
                action = () => Find.LetterStack.RemoveLetter(this)
            };
            yield return Option_Postpone;
        }
    }

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_References.Look(ref targetMap, "caelaviCorrespondentMap");
        Scribe_Values.Look(ref pawnKindDefName, "caelaviCorrespondentPawnKind", "CA_DevelopmentPawn");
    }

    private bool TryAccept()
    {
        Map? map = targetMap;
        PawnKindDef? kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(pawnKindDefName);
        if (map?.IsPlayerHome != true || Faction.OfPlayer == null || kind == null ||
            !RCellFinder.TryFindRandomPawnEntryCell(
                out IntVec3 entryCell, map, CellFinder.EdgeRoadChance_Friendly))
        {
            Log.Warning("[Caelavi] Correspondent accepted, but no player home map, faction, pawn kind, or safe entry cell remained. The offer is kept for retry or decline.");
            return false;
        }

        // Adult and gear are alpha placeholders. The correspondent does not
        // join the republic and is not created until this choice is made.
        Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
            kind,
            Faction.OfPlayer,
            PawnGenerationContext.NonPlayer,
            map.Tile,
            forceGenerateNewPawn: true,
            developmentalStages: DevelopmentalStage.Adult,
            forceNoGear: true));
        GenSpawn.Spawn(pawn, entryCell, map);
        Find.LetterStack.ReceiveLetter(
            "CA_CorrespondentJoinedLabel".Translate(),
            "CA_CorrespondentJoinedText".Translate(),
            LetterDefOf.PositiveEvent,
            pawn);
        return true;
    }
}
