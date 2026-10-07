using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Caelavi;
using RimWorld;
using Verse;

namespace CaelaviSelfTest;

/// <summary>Runs only in an isolated -quicktest game with -caelavi-selftest.</summary>
public sealed class CaelaviSelfTestGameComponent : GameComponent
{
    private const string Prefix = "[CaelaviSelfTest]";
    private const string SaveReloadName = "CaelaviSelfTest-SaveReload";
    private const int SavedIncubationTicks = 12345;
    private bool ran;
    private int passed;
    private int failed;
    private bool saveReloadPending;
    private string savedAdultId = "";
    private string savedMotherId = "";
    private string savedFatherId = "";
    private string savedEggId = "";

    public CaelaviSelfTestGameComponent(Game game)
    {
    }

    public override void StartedNewGame()
    {
        if (ran || !GenCommandLine.CommandLineArgPassed("caelavi-selftest") ||
            !GenCommandLine.CommandLineArgPassed("quicktest"))
        {
            return;
        }
        ran = true;
        Log.Message(Prefix + " START Core/Biotech/Harmony/VEF + Caelavi runtime checks");
        try
        {
            RunChecks();
        }
        catch (Exception ex)
        {
            Fail("unexpected_exception", ex.ToString());
        }
        if (failed == 0)
        {
            try
            {
                PrepareSaveReload();
            }
            catch (Exception ex)
            {
                Fail("save_reload_setup_exception", ex.ToString());
            }
        }
        if (failed != 0 || !saveReloadPending)
        {
            ReportResult();
        }
    }

    public override void ExposeData()
    {
        Scribe_Values.Look(ref passed, "caelaviSelfTestPassed", 0);
        Scribe_Values.Look(ref failed, "caelaviSelfTestFailed", 0);
        Scribe_Values.Look(ref saveReloadPending, "caelaviSelfTestSaveReloadPending", false);
        Scribe_Values.Look(ref savedAdultId, "caelaviSelfTestAdultId", "");
        Scribe_Values.Look(ref savedMotherId, "caelaviSelfTestMotherId", "");
        Scribe_Values.Look(ref savedFatherId, "caelaviSelfTestFatherId", "");
        Scribe_Values.Look(ref savedEggId, "caelaviSelfTestEggId", "");
    }

    public override void LoadedGame()
    {
        if (!saveReloadPending || !GenCommandLine.CommandLineArgPassed("caelavi-selftest") ||
            !GenCommandLine.CommandLineArgPassed("quicktest"))
        {
            return;
        }
        try
        {
            CheckLoadedState();
        }
        catch (Exception ex)
        {
            Fail("save_reload_check_exception", ex.ToString());
        }
        saveReloadPending = false;
        ReportResult();
    }

    private void PrepareSaveReload()
    {
        PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamed("CA_DevelopmentPawn");
        ThingDef eggDef = DefDatabase<ThingDef>.GetNamed("CA_FertilizedEgg");
        HediffDef flightDef = DefDatabase<HediffDef>.GetNamed("CA_DeployedFlight");
        LetterDef letterDef = DefDatabase<LetterDef>.GetNamed("CA_CorrespondentOffer");
        Map? map = Find.CurrentMap;
        Pawn? starter = map?.mapPawns.FreeColonistsSpawned.FirstOrDefault();
        if (map == null || starter == null)
        {
            Fail("save_reload_map", "no quicktest home map or starter pawn");
            return;
        }

        Pawn adult = Generate(kind, 18f, DevelopmentalStage.Adult);
        GenSpawn.Spawn(adult, starter.Position, map);
        CompCaelaviFlight? flight = adult.GetComp<CompCaelaviFlight>();
        Command_Toggle? toggle = flight?.CompGetGizmosExtra().OfType<Command_Toggle>().FirstOrDefault();
        toggle?.toggleAction();
        flight?.Synchronize();
        Check("save_reload_deployed_before_save", adult.Spawned && flight?.Deployed == true &&
              flight.EffectiveWingCount == 2 && StageMatches(FlightHediff(adult, flightDef), 2f));

        Pawn mother = Generate(kind, 20f, DevelopmentalStage.Adult, Gender.Female);
        Pawn father = Generate(kind, 20f, DevelopmentalStage.Adult, Gender.Male);
        GenSpawn.Spawn(mother, starter.Position, map);
        GenSpawn.Spawn(father, starter.Position, map);
        ThingWithComps egg = (ThingWithComps)ThingMaker.MakeThing(eggDef);
        CompCaelaviEgg? embryo = egg.TryGetComp<CompCaelaviEgg>();
        if (embryo == null)
        {
            Fail("save_reload_embryo_comp", "egg has no CompCaelaviEgg");
            return;
        }
        GeneSet genes = PregnancyUtility.GetInheritedGeneSet(father, mother, out _);
        embryo.Initialize(mother, father, mother.Faction, genes);
        FieldInfo incubation = typeof(CompCaelaviEgg).GetField(
            "incubationTicks", BindingFlags.Instance | BindingFlags.NonPublic)!;
        incubation.SetValue(embryo, SavedIncubationTicks);
        bool eggPlaced = GenPlace.TryPlaceThing(egg, starter.Position, map, ThingPlaceMode.Near);
        Check("save_reload_egg_before_save", eggPlaced && egg.Spawned &&
              egg.TryGetComp<CompHasPawnSources>()?.pawnSources.Contains(mother) == true &&
              egg.TryGetComp<CompHasPawnSources>()?.pawnSources.Contains(father) == true);

        ChoiceLetter_CaelaviCorrespondent? letter =
            LetterMaker.MakeLetter("Caelavi self-test", "Pending save and reload.", letterDef)
                as ChoiceLetter_CaelaviCorrespondent;
        if (letter == null)
        {
            Fail("save_reload_letter_create", "custom choice letter was not created");
            return;
        }
        letter.targetMap = map;
        letter.pawnKindDefName = kind.defName;
        Find.LetterStack.ReceiveLetter(letter, playSound: false);
        Check("save_reload_letter_before_save", Find.LetterStack.LettersListForReading.Contains(letter));

        if (failed != 0)
        {
            return;
        }
        savedAdultId = adult.ThingID;
        savedMotherId = mother.ThingID;
        savedFatherId = father.ThingID;
        savedEggId = egg.ThingID;
        saveReloadPending = true;
        GameDataSaveLoader.SaveGame(SaveReloadName);
        string path = GenFilePaths.FilePathForSavedGame(SaveReloadName);
        Check("isolated_save_written", File.Exists(path), path);
        if (failed != 0)
        {
            saveReloadPending = false;
            return;
        }
        Log.Message($"{Prefix} PHASE1 passed={passed} failures={failed} save={path}");
        // StartedNewGame runs inside Core's quicktest long event. Schedule the
        // load after it finishes so no active initialization frame is disposed.
        LongEventHandler.ExecuteWhenFinished(() => GameDataSaveLoader.LoadGame(SaveReloadName));
    }

    private void CheckLoadedState()
    {
        Map? map = Find.CurrentMap;
        Check("save_reload_map_loaded", map != null);
        if (map == null)
        {
            return;
        }
        Pawn? adult = map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == savedAdultId);
        Pawn? mother = map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == savedMotherId);
        Pawn? father = map.mapPawns.AllPawnsSpawned.FirstOrDefault(p => p.ThingID == savedFatherId);
        ThingDef eggDef = DefDatabase<ThingDef>.GetNamed("CA_FertilizedEgg");
        Thing? egg = map.listerThings.ThingsOfDef(eggDef).FirstOrDefault(t => t.ThingID == savedEggId);
        Check("save_reload_objects_found", adult != null && mother != null && father != null && egg != null);
        if (adult == null || mother == null || father == null || egg == null)
        {
            return;
        }
        HediffDef flightDef = DefDatabase<HediffDef>.GetNamed("CA_DeployedFlight");
        CompCaelaviFlight? flight = adult.GetComp<CompCaelaviFlight>();
        Check("save_reload_flight_state", flight?.Deployed == true &&
              flight.EffectiveWingCount == 2 && StageMatches(FlightHediff(adult, flightDef), 2f));

        CompCaelaviEgg? embryo = egg.TryGetComp<CompCaelaviEgg>();
        FieldInfo incubation = typeof(CompCaelaviEgg).GetField(
            "incubationTicks", BindingFlags.Instance | BindingFlags.NonPublic)!;
        FieldInfo motherField = typeof(CompCaelaviEgg).GetField(
            "mother", BindingFlags.Instance | BindingFlags.NonPublic)!;
        FieldInfo fatherField = typeof(CompCaelaviEgg).GetField(
            "father", BindingFlags.Instance | BindingFlags.NonPublic)!;
        Check("save_reload_egg_progress", embryo != null && egg.Spawned &&
              (int)incubation.GetValue(embryo)! == SavedIncubationTicks);
        Check("save_reload_egg_parents", embryo != null &&
              ReferenceEquals(motherField.GetValue(embryo), mother) &&
              ReferenceEquals(fatherField.GetValue(embryo), father) &&
              egg.TryGetComp<CompHasPawnSources>()?.pawnSources.Contains(mother) == true &&
              egg.TryGetComp<CompHasPawnSources>()?.pawnSources.Contains(father) == true);

        ChoiceLetter_CaelaviCorrespondent? letter = Find.LetterStack.LettersListForReading
            .OfType<ChoiceLetter_CaelaviCorrespondent>().FirstOrDefault();
        Check("save_reload_choice_letter", letter != null &&
              ReferenceEquals(letter.targetMap, map) &&
              letter.pawnKindDefName == "CA_DevelopmentPawn" &&
              letter.Choices.Count() == 3);
    }

    private void ReportResult() =>
        Log.Message($"{Prefix} RESULT {(failed == 0 ? "PASS" : "FAIL")} passed={passed} failures={failed}");

    private void CheckXenogermMorphology(PawnKindDef kind, GeneDef morphology)
    {
        Pawn recipient = Generate(kind, 18f, DevelopmentalStage.Adult);
        GeneDef thin = DefDatabase<GeneDef>.GetNamed("Body_Thin");
        GeneDef darkVision = DefDatabase<GeneDef>.GetNamed("DarkVision");
        Gene originalMarker = recipient.genes.GetGene(morphology);
        Genepack pack = (Genepack)ThingMaker.MakeThing(ThingDefOf.Genepack);
        pack.Initialize(new List<GeneDef> { thin });
        Xenogerm implant = (Xenogerm)ThingMaker.MakeThing(ThingDefOf.Xenogerm);
        implant.Initialize(new List<Genepack> { pack }, "Caelavi morphology regression", null);
        GeneUtility.ImplantXenogermItem(recipient, implant);
        Check("implant_restores_racial_marker", recipient.genes.GetGene(morphology) != null &&
              !ReferenceEquals(originalMarker, recipient.genes.GetGene(morphology)) &&
              recipient.genes.Xenogenes.Count(g => g.def == morphology) == 1 &&
              recipient.genes.Endogenes.All(g => g.def != morphology));
        Check("implant_preserves_body_gene", recipient.genes.GetGene(thin)?.Active == true &&
              recipient.story.bodyType == BodyTypeDefOf.Thin);

        Pawn donor = Generate(PawnKindDefOf.Colonist, 18f, DevelopmentalStage.Adult);
        donor.genes.ClearXenogenes();
        donor.genes.AddGene(darkVision, xenogene: true);
        GeneUtility.ReimplantXenogerm(donor, recipient);
        Check("reimplant_restores_racial_marker", recipient.genes.Xenogenes.Count(g => g.def == morphology) == 1 &&
              recipient.genes.Endogenes.All(g => g.def != morphology) &&
              recipient.genes.GetGene(darkVision)?.Active == true &&
              recipient.genes.GetGene(thin) == null &&
              recipient.story.bodyType.defName == "CA_AlphaBody");

        Pawn human = Generate(PawnKindDefOf.Colonist, 18f, DevelopmentalStage.Adult);
        GeneUtility.ImplantXenogermItem(human, implant);
        Check("human_implant_no_racial_marker", human.genes.GetGene(morphology) == null);
        GeneUtility.ReimplantXenogerm(donor, human);
        Check("human_reimplant_no_racial_marker", human.genes.GetGene(morphology) == null &&
              human.genes.GetGene(darkVision)?.Active == true);
    }

    private void RunChecks()
    {
        PawnKindDef? kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("CA_DevelopmentPawn");
        ThingDef? race = DefDatabase<ThingDef>.GetNamedSilentFail("CA_Caelavi");
        BodyPartDef? wingDef = DefDatabase<BodyPartDef>.GetNamedSilentFail("CA_Wing");
        BodyPartGroupDef? wingGroup = DefDatabase<BodyPartGroupDef>.GetNamedSilentFail("CA_Wings");
        GeneDef? morphology = DefDatabase<GeneDef>.GetNamedSilentFail("CA_AlphaMorphologyGene");
        HediffDef? flightDef = DefDatabase<HediffDef>.GetNamedSilentFail("CA_DeployedFlight");
        Check("defs_loaded", kind != null && race != null && wingDef != null &&
                              wingGroup != null && morphology != null && flightDef != null);
        if (kind == null || race == null || wingDef == null || wingGroup == null ||
            morphology == null || flightDef == null)
        {
            return;
        }

        Pawn adult = Generate(kind, 18f, DevelopmentalStage.Adult);
        Check("adult_generated", adult != null);
        if (adult == null)
        {
            return;
        }
        Check("race", adult.def == race && adult.kindDef == kind);
        Check("adult_age_18", Math.Abs(adult.ageTracker.AgeBiologicalYearsFloat - 18f) < 0.05f,
              $"actual={adult.ageTracker.AgeBiologicalYearsFloat:F2}");
        List<BodyPartRecord> wings = adult.RaceProps.body.AllParts
            .Where(part => part.def == wingDef).ToList();
        Check("two_distinct_wings", wings.Count == 2 &&
              wings.Select(part => part.customLabel).Distinct().Count() == 2 &&
              wings.All(part => part.groups.Contains(wingGroup)),
              "records=" + string.Join(",", wings.Select(part => part.customLabel ?? "?")));
        Check("morphology_gene", adult.genes?.GetGene(morphology) != null);
        CheckXenogermMorphology(kind, morphology);
        CompCaelaviFlight? flight = adult.GetComp<CompCaelaviFlight>();
        Check("flight_comp", flight != null);
        if (flight == null || wings.Count != 2)
        {
            return;
        }

        Check("initial_retracted", !flight.Deployed && flight.EffectiveWingCount == 0 &&
              FlightHediff(adult, flightDef) == null);
        Command_Toggle? toggle = flight.CompGetGizmosExtra().OfType<Command_Toggle>().FirstOrDefault();
        Check("manual_toggle_available", toggle != null);
        if (toggle == null)
        {
            return;
        }
        toggle.toggleAction();
        flight.Synchronize();
        Check("two_wing_flight", flight.Deployed && flight.EffectiveWingCount == 2 &&
              StageMatches(FlightHediff(adult, flightDef), 2f));

        ThingDef? guardDef = DefDatabase<ThingDef>.GetNamedSilentFail("CA_WingGuardAlpha");
        if (guardDef != null)
        {
            Apparel guard = (Apparel)ThingMaker.MakeThing(guardDef);
            adult.apparel.Wear(guard);
            flight.Synchronize();
            Check("wing_guard_suppresses_flight", flight.Deployed &&
                  adult.apparel.WornApparel.Contains(guard) &&
                  flight.EffectiveWingCount == 0 && FlightHediff(adult, flightDef) == null);
            adult.apparel.Remove(guard);
            flight.Synchronize();
            Check("wing_guard_removed_restores_flight", flight.EffectiveWingCount == 2 &&
                  StageMatches(FlightHediff(adult, flightDef), 2f));
        }
        else
        {
            Fail("wing_guard_def", "CA_WingGuardAlpha missing");
        }

        adult.health.AddHediff(HediffDefOf.MissingBodyPart, wings[0]);
        flight.Synchronize();
        Check("one_wing_flight", adult.health.hediffSet.PartIsMissing(wings[0]) &&
              !adult.health.hediffSet.PartIsMissing(wings[1]) &&
              flight.EffectiveWingCount == 1 && StageMatches(FlightHediff(adult, flightDef), 1f));

        adult.health.AddHediff(HediffDefOf.MissingBodyPart, wings[1]);
        flight.Synchronize();
        Check("zero_wing_no_flight", adult.health.hediffSet.PartIsMissing(wings[0]) &&
              adult.health.hediffSet.PartIsMissing(wings[1]) &&
              flight.Deployed && flight.EffectiveWingCount == 0 &&
              FlightHediff(adult, flightDef) == null);

        Pawn child = Generate(kind, 12f, DevelopmentalStage.Child);
        Check("child_generated", child != null);
        if (child != null)
        {
            CompCaelaviFlight? childFlight = child.GetComp<CompCaelaviFlight>();
            Check("child_age_gate", childFlight != null &&
                  Math.Abs(child.ageTracker.AgeBiologicalYearsFloat - 12f) < 0.05f &&
                  childFlight.EffectiveWingCount == 0 &&
                  FlightHediff(child, flightDef) == null);
        }

        Faction? republic = Find.FactionManager.AllFactions.FirstOrDefault(
            faction => faction.def.defName == "CA_DemocraticRepublic");
        Check("republic_world_faction", republic != null);
        if (republic != null)
        {
            Check("republic_initial_neutral",
                  republic.RelationKindWith(Faction.OfPlayer) == FactionRelationKind.Neutral &&
                  republic.GoodwillWith(Faction.OfPlayer) == 0,
                  "goodwill=" + republic.GoodwillWith(Faction.OfPlayer));
        }

        RunEggChecks(kind, race, morphology);
    }

    private void RunEggChecks(PawnKindDef kind, ThingDef race, GeneDef morphology)
    {
        ThingDef? eggDef = DefDatabase<ThingDef>.GetNamedSilentFail("CA_FertilizedEgg");
        HediffDef? pregnancyDef = DefDatabase<HediffDef>.GetNamedSilentFail("PregnantHuman");
        Check("egg_defs_and_six_day_gestation", eggDef != null && pregnancyDef != null &&
              Math.Abs(race.race.gestationPeriodDays - 6f) < 0.01f);
        if (eggDef == null || pregnancyDef == null)
        {
            return;
        }

        Map? map = Find.CurrentMap;
        Pawn? starter = map?.mapPawns.FreeColonistsSpawned.FirstOrDefault();
        Check("egg_test_map", map != null && starter != null);
        if (map == null || starter == null)
        {
            return;
        }

        Pawn mother = Generate(kind, 20f, DevelopmentalStage.Adult, Gender.Female);
        Pawn father = Generate(kind, 20f, DevelopmentalStage.Adult, Gender.Male);
        GenSpawn.Spawn(mother, starter.Position, map);
        GenSpawn.Spawn(father, starter.Position, map);
        Check("egg_parents_generated", mother.Spawned && father.Spawned &&
              mother.def == race && father.def == race);

        GeneSet inherited = PregnancyUtility.GetInheritedGeneSet(father, mother, out _);
        Hediff_Pregnant pregnancy = (Hediff_Pregnant)mother.health.AddHediff(pregnancyDef);
        pregnancy.SetParents(mother, father, inherited);
        pregnancy.TickInterval(6 * 60000);

        List<Thing> eggs = map.listerThings.ThingsOfDef(eggDef).ToList();
        Check("six_day_labor_lays_one_to_three_eggs",
              eggs.Count >= 1 && eggs.Count <= 3 &&
              mother.health.hediffSet.GetFirstHediffOfDef(pregnancyDef) == null &&
              mother.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PregnancyLabor) == null,
              "count=" + eggs.Count);
        if (eggs.Count == 0)
        {
            return;
        }
        Check("separate_eggs_and_parent_sources", eggs.All(egg =>
              egg.stackCount == 1 && egg.TryGetComp<CompCaelaviEgg>() != null &&
              egg.TryGetComp<CompHasPawnSources>()?.pawnSources.Contains(mother) == true &&
              egg.TryGetComp<CompHasPawnSources>()?.pawnSources.Contains(father) == true));

        // Advance each egg to the last tick, then exercise its actual CompTick
        // hatch path. This checks the 12-day threshold without waiting 720000
        // real game ticks; long incubation and save/reload remain separate tests.
        FieldInfo? incubation = typeof(CompCaelaviEgg).GetField(
            "incubationTicks", BindingFlags.Instance | BindingFlags.NonPublic);
        Check("hatch_tick_access", incubation != null);
        if (incubation == null)
        {
            return;
        }
        HashSet<Pawn> before = new HashSet<Pawn>(map.mapPawns.AllPawnsSpawned);
        int hatchTicks = (int)(eggDef.GetCompProperties<CompProperties_CaelaviEgg>().daysToHatch * 60000f);
        foreach (Thing egg in eggs)
        {
            CompCaelaviEgg embryo = egg.TryGetComp<CompCaelaviEgg>();
            incubation.SetValue(embryo, hatchTicks - 1);
            embryo.CompTick();
        }
        List<Pawn> hatchlings = map.mapPawns.AllPawnsSpawned
            .Where(pawn => !before.Contains(pawn) && pawn.def == race).ToList();
        Check("twelve_day_hatch_count", hatchlings.Count == eggs.Count &&
              eggs.All(egg => egg.Destroyed),
              "eggs=" + eggs.Count + " hatchlings=" + hatchlings.Count);
        Check("hatchling_age_gene_and_parents", hatchlings.Count == eggs.Count &&
              hatchlings.All(child =>
                  Math.Abs(child.ageTracker.AgeBiologicalYearsFloat - 3f) < 0.05f &&
                  child.genes?.GetGene(morphology) != null &&
                  child.relations.DirectRelationExists(PawnRelationDefOf.Parent, mother) &&
                  child.relations.DirectRelationExists(PawnRelationDefOf.Parent, father)));
    }

    private static Pawn Generate(PawnKindDef kind, float age, DevelopmentalStage stage,
                                 Gender? gender = null)
    {
        PawnGenerationRequest request = new PawnGenerationRequest(
            kind, Faction.OfPlayer, PawnGenerationContext.NonPlayer,
            forceGenerateNewPawn: true, canGeneratePawnRelations: false,
            fixedBiologicalAge: age, fixedChronologicalAge: age,
            fixedGender: gender, developmentalStages: stage, forceNoGear: true);
        return PawnGenerator.GeneratePawn(request);
    }

    private static Hediff? FlightHediff(Pawn pawn, HediffDef def) =>
        pawn.health.hediffSet.GetFirstHediffOfDef(def);

    private static bool StageMatches(Hediff? hediff, float severity) =>
        hediff != null && Math.Abs(hediff.Severity - severity) < 0.01f &&
        hediff.CurStage != null && Math.Abs(hediff.CurStage.minSeverity - severity) < 0.01f;

    private void Check(string name, bool okay, string detail = "")
    {
        if (okay)
        {
            passed++;
            Log.Message($"{Prefix} PASS {name}{(detail.Length == 0 ? "" : " " + detail)}");
        }
        else
        {
            Fail(name, detail);
        }
    }

    private void Fail(string name, string detail)
    {
        failed++;
        Log.Error($"{Prefix} FAIL {name}{(detail.Length == 0 ? "" : " " + detail)}");
    }
}
