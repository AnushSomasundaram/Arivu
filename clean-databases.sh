#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Clean Arivu Databases and Data
# ═══════════════════════════════════════════════════════════════════════════
# Removes all database files and cached data for a fresh build
# ═══════════════════════════════════════════════════════════════════════════

set -e

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  Cleaning Arivu Databases & Data      ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# ── Clean Backend Data Directory ─────────────────────────────────────────────
echo -e "${YELLOW}[1/4] Cleaning backend data directory...${NC}"

if [ -d "Arivu/Backend/data" ]; then
    echo "  Removing: Arivu/Backend/data/"
    rm -rf Arivu/Backend/data
    echo -e "${GREEN}  ✓ Backend data directory removed${NC}"
else
    echo -e "  ℹ No backend data directory found"
fi
echo ""

# ── Clean User Home Directory ────────────────────────────────────────────────
echo -e "${YELLOW}[2/4] Cleaning user data directory...${NC}"

if [ -d "$HOME/.arivu" ]; then
    echo "  Removing: ~/.arivu/"
    rm -rf "$HOME/.arivu"
    echo -e "${GREEN}  ✓ User data directory removed${NC}"
else
    echo -e "  ℹ No user data directory found"
fi
echo ""

# ── Clean ChromaDB Data ───────────────────────────────────────────────────────
echo -e "${YELLOW}[3/4] Cleaning ChromaDB data...${NC}"

# Check for chroma data in various possible locations
CHROMA_LOCATIONS=(
    "Arivu/Backend/chroma"
    "Arivu/Backend/.chroma"
    "$HOME/.chroma"
)

FOUND_CHROMA=false
for location in "${CHROMA_LOCATIONS[@]}"; do
    if [ -d "$location" ]; then
        echo "  Removing: $location"
        rm -rf "$location"
        FOUND_CHROMA=true
    fi
done

if [ "$FOUND_CHROMA" = true ]; then
    echo -e "${GREEN}  ✓ ChromaDB data removed${NC}"
else
    echo -e "  ℹ No ChromaDB data found"
fi
echo ""

# ── Clean Build Artifacts ─────────────────────────────────────────────────────
echo -e "${YELLOW}[4/4] Cleaning build artifacts...${NC}"

# Clean backend build
if [ -d "Arivu/Backend/dist" ]; then
    echo "  Removing: Arivu/Backend/dist/"
    rm -rf Arivu/Backend/dist
fi

if [ -d "Arivu/Backend/build" ]; then
    echo "  Removing: Arivu/Backend/build/"
    rm -rf Arivu/Backend/build
fi

# Clean frontend builds
if [ -d "Arivu/Frontend/vue-project/dist" ]; then
    echo "  Removing: Arivu/Frontend/vue-project/dist/"
    rm -rf Arivu/Frontend/vue-project/dist
fi

if [ -d "Arivu/Frontend/vue-project/electron/dist" ]; then
    echo "  Removing: Arivu/Frontend/vue-project/electron/dist/"
    rm -rf Arivu/Frontend/vue-project/electron/dist
fi

# Clean release builds
if [ -d "Arivu/Frontend/vue-project/release" ]; then
    echo "  Removing: Arivu/Frontend/vue-project/release/"
    rm -rf Arivu/Frontend/vue-project/release
fi

echo -e "${GREEN}  ✓ Build artifacts removed${NC}"
echo ""

# ── Summary ──────────────────────────────────────────────────────────────────
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Cleanup Complete!                  ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "Cleaned:"
echo "  • Backend database (data/arivu.db)"
echo "  • User data (~/.arivu/)"
echo "  • Vector store data (ChromaDB)"
echo "  • Build artifacts (dist/, build/)"
echo ""
echo -e "${BLUE}Ready for a fresh build!${NC}"
echo ""
