using HarmonyLib;
using RimWorld;
using Verse;

namespace Caelavi;

/// <summary>
/// The shared feathers are a property of the race, independent of the pawn's
/// Biotech xenotype. They are installed as a non-inheritable xenogene so a
/// human child of a Caelavi father does not inherit Caelavi appearance.
/// </summary>
internal static class CaelaviMorphology
{
    private const string RaceDefName = "CA_Caelavi";
    private const string GeneDefName = "CA_AlphaMorphologyGene";
    private const string AdultBodyDefName = "CA_AlphaBody";
    private static bool missingGeneReported;
    private static bool missingBodyReported;

    internal static void Ensure(Pawn? pawn)
    {
        if (pawn?.def?.defName != RaceDefName || !ModsConfig.BiotechActive || pawn.genes == null)
        {
            return;
        }

        GeneDef geneDef = DefDatabase<GeneDef>.GetNamedSilentFail(GeneDefName);
        if (geneDef == null)
        {
            if (!missingGeneReported)
            {
                missingGeneReported = true;
                Log.Error("[Caelavi] Missing CA_AlphaMorphologyGene; shared feathers cannot be rendered.");
            }
            return;
        }

        if (pawn.genes.GetGene(geneDef) == null)
        {
            pawn.genes.AddGene(geneDef, xenogene: true);
        }

        // GeneDef.bodyType accepts only vanilla GeneticBodyType enum values.
        // Keep this race's alpha body on adults while allowing other active
        // Biotech body-type genes to express their phenotype. Juveniles keep
        // the game's age-specific body type until new child art is authored.
        if (pawn.DevelopmentalStage != DevelopmentalStage.Adult || pawn.story == null)
        {
            return;
        }
        foreach (Gene gene in pawn.genes.GenesListForReading)
        {
            if (gene.Active && gene.def != geneDef && gene.def.bodyType.HasValue)
            {
                return;
            }
        }

        BodyTypeDef bodyDef = DefDatabase<BodyTypeDef>.GetNamedSilentFail(AdultBodyDefName);
        if (bodyDef == null)
        {
            if (!missingBodyReported)
            {
                missingBodyReported = true;
                Log.Error("[Caelavi] Missing CA_AlphaBody; the adult alpha body cannot be rendered.");
            }
            return;
        }
        if (pawn.story.bodyType != bodyDef)
        {
            pawn.story.bodyType = bodyDef;
            pawn.Drawer.renderer.SetAllGraphicsDirty();
        }
    }
}

// GenerateGenes runs after vanilla xenotype selection and before the remaining
// generation work. This covers newly generated adults and children.
[HarmonyPatch(typeof(PawnGenerator), "GenerateGenes")]
internal static class CaelaviGenerateGenesPatch
{
    private static void Postfix(Pawn pawn) => CaelaviMorphology.Ensure(pawn);
}

// GeneratePawn may return a redressed world pawn without calling GenerateGenes.
[HarmonyPatch(typeof(PawnGenerator), nameof(PawnGenerator.GeneratePawn),
    new[] { typeof(PawnGenerationRequest) })]
internal static class CaelaviGeneratePawnPatch
{
    private static void Postfix(Pawn __result) => CaelaviMorphology.Ensure(__result);
}

// Implantation replaces the entire xenogene set. Restore the non-inheritable
// racial marker after vanilla finishes adding genes and updating the body.
[HarmonyPatch(typeof(GeneUtility), nameof(GeneUtility.ImplantXenogermItem))]
internal static class CaelaviImplantXenogermPatch
{
    private static void Postfix(Pawn pawn) => CaelaviMorphology.Ensure(pawn);
}

// The gene reimplantation ability uses a separate vanilla replacement path.
[HarmonyPatch(typeof(GeneUtility), nameof(GeneUtility.ReimplantXenogerm))]
internal static class CaelaviReimplantXenogermPatch
{
    private static void Postfix(Pawn recipient) => CaelaviMorphology.Ensure(recipient);
}

// Saves made before this guarantee was added can lack the appearance gene.
[HarmonyPatch(typeof(Pawn), nameof(Pawn.ExposeData))]
internal static class CaelaviPawnLoadPatch
{
    private static void Postfix(Pawn __instance)
    {
        if (Scribe.mode == LoadSaveMode.PostLoadInit)
        {
            CaelaviMorphology.Ensure(__instance);
        }
    }
}

// Vanilla replaces Child/Baby body types on the transition to adulthood.
// Reapply the race's alpha adult body after that replacement.
[HarmonyPatch(typeof(LifeStageWorker_HumanlikeAdult), nameof(LifeStageWorker_HumanlikeAdult.Notify_LifeStageStarted))]
internal static class CaelaviAdultLifeStagePatch
{
    private static void Postfix(Pawn pawn) => CaelaviMorphology.Ensure(pawn);
}
