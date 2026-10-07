#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(dirname "$SCRIPT_DIR")
DOTNET_BIN=${DOTNET_BIN:-dotnet}
GAME_APP=${RIMWORLD_APP:-"$HOME/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app"}
WORKSHOP_DIR=${RIMWORLD_WORKSHOP_DIR:-"$HOME/Library/Application Support/Steam/steamapps/workshop/content/294100"}
MANAGED_DIR=${RIMWORLD_MANAGED_DIR:-"$GAME_APP/Contents/Resources/Data/Managed"}
HARMONY_PATH=${HARMONY_DLL:-"$WORKSHOP_DIR/2009463077/Current/Assemblies/0Harmony.dll"}
VEF_PATH=${VEF_DLL:-"$WORKSHOP_DIR/2023507013/1.6/Assemblies/VEF.dll"}

"$DOTNET_BIN" build "$ROOT_DIR/Source/Caelavi.csproj" --configuration Release \
  -p:RimWorldManagedDir="$MANAGED_DIR" \
  -p:HarmonyDll="$HARMONY_PATH" \
  -p:VefDll="$VEF_PATH"
