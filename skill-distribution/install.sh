#!/usr/bin/env sh
# install.sh — AgenticNFT Mint Skill installer
# Installs the okx-agentic-nft-mint skill for Claude Code and compatible agent systems.
#
# Usage (once hosted on GitHub):
#   curl -sSL https://raw.githubusercontent.com/YunanL/aw-nft/main/skill-distribution/install.sh | sh
#
# Or locally:
#   sh skill-distribution/install.sh

set -e

SKILL_NAME="okx-agentic-nft-mint"
SKILL_VERSION="1.0.0"

# ── Colour helpers ──────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { printf "${CYAN}[info]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[ok]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[warn]${NC}  %s\n" "$1"; }
error()   { printf "${RED}[error]${NC} %s\n" "$1" >&2; }

printf "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${CYAN}  AgenticNFT Mint Skill  v${SKILL_VERSION}${NC}\n"
printf "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n\n"

# ── Step 1: Locate SKILL.md ─────────────────────────────────────────────────
# Detect if running from local checkout or piped from curl
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "")"
SKILL_MD=""

if [ -f "${SCRIPT_DIR}/SKILL.md" ]; then
  SKILL_MD="${SCRIPT_DIR}/SKILL.md"
  info "Using local SKILL.md from ${SCRIPT_DIR}"
else
  # Download from GitHub
  GITHUB_RAW="https://raw.githubusercontent.com/YunanL/aw-nft/main/skill-distribution/SKILL.md"
  TMP_SKILL="/tmp/${SKILL_NAME}-SKILL.md"
  info "Downloading SKILL.md..."
  if ! curl -sSL --fail "${GITHUB_RAW}" -o "${TMP_SKILL}" 2>/dev/null; then
    error "Failed to download SKILL.md from GitHub."
    error "Please run from the project directory: sh skill-distribution/install.sh"
    exit 1
  fi
  SKILL_MD="${TMP_SKILL}"
fi

# ── Step 2: Install for Claude Code (~/.claude/skills/) ─────────────────────
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
info "Installing to Claude Code skills: ${CLAUDE_SKILLS_DIR}"
mkdir -p "${CLAUDE_SKILLS_DIR}"
cp "${SKILL_MD}" "${CLAUDE_SKILLS_DIR}/SKILL.md"
success "Installed to ${CLAUDE_SKILLS_DIR}/SKILL.md"

# ── Step 3: Install for agent systems (~/.agents/skills/) ────────────────────
AGENTS_SKILLS_DIR="${HOME}/.agents/skills/${SKILL_NAME}"
if [ -d "${HOME}/.agents/skills" ]; then
  info "Installing to agent skills: ${AGENTS_SKILLS_DIR}"
  mkdir -p "${AGENTS_SKILLS_DIR}"
  cp "${SKILL_MD}" "${AGENTS_SKILLS_DIR}/SKILL.md"
  success "Installed to ${AGENTS_SKILLS_DIR}/SKILL.md"
fi

# ── Step 4: Check onchainos ──────────────────────────────────────────────────
printf "\n"
if command -v onchainos >/dev/null 2>&1; then
  ONCHAINOS_VER=$(onchainos --version 2>/dev/null || echo "unknown")
  success "onchainos is installed (${ONCHAINOS_VER})"
else
  warn "onchainos CLI not found. The skill requires it to mint."
  printf "\n  Install onchainos:\n"
  printf "  ${CYAN}curl -sSL \"\$(curl -sSL https://api.github.com/repos/okx/onchainos-skills/releases/latest | grep -o 'https://raw.githubusercontent.com[^\"]*install.sh')\" | sh${NC}\n\n"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
printf "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  Skill installed successfully!${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n\n"
printf "  Next steps:\n"
printf "  1. Open Claude Code in any directory\n"
printf "  2. Say: ${CYAN}\"mint my AgenticNFT\"${NC}\n"
printf "  3. Claude will use the skill automatically ✨\n\n"
printf "  Contract: ${CYAN}0x5f349ea7dD0ab6b4533f6178e8a4674eb42cD01B${NC}\n"
printf "  Network:  X Layer Mainnet (chainId 196) · gas-free\n\n"
