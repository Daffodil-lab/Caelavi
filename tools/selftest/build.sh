#!/bin/sh
set -eu

SELFTEST_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(dirname "$(dirname "$SELFTEST_DIR")")
DOTNET_BIN=${DOTNET_BIN:-dotnet}
GAME_APP=${RIMWORLD_APP:-"$HOME/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app"}
MANAGED_DIR=${RIMWORLD_MANAGED_DIR:-"$GAME_APP/Contents/Resources/Data/Managed"}

"$DOTNET_BIN" build "$SELFTEST_DIR/Source/Caelavi.SelfTest.csproj" --configuration Release \
  -p:RimWorldManagedDir="$MANAGED_DIR" \
  -p:CaelaviAssembly="$ROOT_DIR/1.6/Assemblies/Caelavi.dll"
