using System;
using RimWorld;
using Verse;

namespace Caelavi;

/// <summary>Side and posture for one of the four alpha wing render nodes.</summary>
public sealed class CaelaviWingRenderNodeProperties : PawnRenderNodeProperties
{
    public bool leftWing;
    public bool deployedWing;
}

/// <summary>
/// Use the same anatomical wing records as health and flight. Each side has a
/// folded and deployed texture; only the intact side's current posture draws.
/// </summary>
public sealed class CaelaviWingRenderNodeWorker : PawnRenderNodeWorker_AttachmentBody
{
    public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
    {
        if (!base.CanDrawNow(node, parms) ||
            node.Props is not CaelaviWingRenderNodeProperties props)
        {
            return false;
        }

        Pawn? pawn = parms.pawn;
        if (pawn?.def?.defName != "CA_Caelavi" || pawn.health?.hediffSet == null)
        {
            return false;
        }

        bool deployed = pawn.GetComp<CompCaelaviFlight>()?.Deployed == true;
        if (props.deployedWing != deployed)
        {
            return false;
        }

        BodyPartDef wingDef = DefDatabase<BodyPartDef>.GetNamedSilentFail("CA_Wing");
        if (wingDef == null)
        {
            return false;
        }

        string sideLabel = props.leftWing ? "left wing" : "right wing";
        foreach (BodyPartRecord part in pawn.RaceProps.body.GetPartsWithDef(wingDef))
        {
            if (string.Equals(part.customLabel, sideLabel, StringComparison.Ordinal))
            {
                // A wounded but present wing remains visible. A missing wing,
                // whether amputated or destroyed by damage, does not draw.
                return !pawn.health.hediffSet.PartIsMissing(part);
            }
        }

        return false;
    }
}
