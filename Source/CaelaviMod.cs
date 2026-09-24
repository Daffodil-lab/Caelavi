using HarmonyLib;
using Verse;

namespace Caelavi;

/// <summary>Entry point for features that cannot be expressed with game Defs.</summary>
public sealed class CaelaviMod : Mod
{
    public CaelaviMod(ModContentPack content) : base(content)
    {
        new Harmony("DaffodilLab.Caelavi").PatchAll(typeof(CaelaviMod).Assembly);
        Log.Message("[Caelavi] Alpha assembly loaded.");
    }
}
