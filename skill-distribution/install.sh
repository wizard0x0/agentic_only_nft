#!/usr/bin/env sh
# install.sh — Club of Agent Mint Skill installer
# Universal: installs for Claude Code, Cursor, Windsurf, and any agent that
# reads from ~/.agent-skills/
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/wizard0x0/agentic_only_nft/main/skill-distribution/install.sh | sh
#
# Or locally:
#   sh skill-distribution/install.sh

set -e

SKILL_NAME="club-of-agent-mint"
SKILL_VERSION="2.0.0"
GITHUB_RAW="https://raw.githubusercontent.com/wizard0x0/agentic_only_nft/main/skill-distribution/SKILL.md"

# ── Colour helpers ───────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
info()    { printf "${CYAN}[info]${NC}  %s\n" "$1"; }
success() { printf "${GREEN}[ok]${NC}    %s\n" "$1"; }
warn()    { printf "${YELLOW}[warn]${NC}  %s\n" "$1"; }
skip()    { printf "${YELLOW}[skip]${NC}  %s\n" "$1"; }

printf "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${CYAN}  Club of Agent — Mint Skill  v${SKILL_VERSION}${NC}\n"
printf "${CYAN}  Universal agent skill installer${NC}\n"
printf "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n\n"

# ── Step 1: Locate SKILL.md ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "")"
SKILL_MD=""

if [ -f "${SCRIPT_DIR}/SKILL.md" ]; then
  SKILL_MD="${SCRIPT_DIR}/SKILL.md"
  info "Using local SKILL.md"
else
  TMP_SKILL="/tmp/${SKILL_NAME}-SKILL.md"
  info "Downloading SKILL.md from GitHub..."
  if ! curl -sSL --fail "${GITHUB_RAW}" -o "${TMP_SKILL}" 2>/dev/null; then
    printf "${RED}[error]${NC} Failed to download SKILL.md.\n" >&2
    exit 1
  fi
  SKILL_MD="${TMP_SKILL}"
fi

INSTALLED=0

# ── Step 2: Claude Code ──────────────────────────────────────────────────────
CLAUDE_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
info "Installing for Claude Code → ${CLAUDE_DIR}"
mkdir -p "${CLAUDE_DIR}"
cp "${SKILL_MD}" "${CLAUDE_DIR}/SKILL.md"
success "Claude Code: ${CLAUDE_DIR}/SKILL.md"
INSTALLED=$((INSTALLED+1))

# ── Step 3: Universal ~/.agent-skills/ (any agent that reads this dir) ───────
UNIVERSAL_DIR="${HOME}/.agent-skills/${SKILL_NAME}"
info "Installing to universal skill store → ${UNIVERSAL_DIR}"
mkdir -p "${UNIVERSAL_DIR}"
cp "${SKILL_MD}" "${UNIVERSAL_DIR}/SKILL.md"
success "Universal: ${UNIVERSAL_DIR}/SKILL.md"
INSTALLED=$((INSTALLED+1))

# ── Step 4: OpenClaw (~/.openclaw/workspace/skills/) ────────────────────────
OPENCLAW_DIR="${HOME}/.openclaw/workspace/skills/${SKILL_NAME}"
if [ -d "${HOME}/.openclaw" ]; then
  mkdir -p "${OPENCLAW_DIR}"
  cp "${SKILL_MD}" "${OPENCLAW_DIR}/SKILL.md"
  success "OpenClaw: ${OPENCLAW_DIR}/SKILL.md"
  INSTALLED=$((INSTALLED+1))
else
  skip "OpenClaw not found (${HOME}/.openclaw missing)"
fi

# ── Step 5: Cursor (.cursor/rules/) ─────────────────────────────────────────
CURSOR_DIR="${HOME}/.cursor/rules"
if [ -d "${HOME}/.cursor" ]; then
  mkdir -p "${CURSOR_DIR}"
  # Cursor uses .mdc format — wrap SKILL.md content
  printf "---\ndescription: Club of Agent mint skill — mint Agentic NFT on X Layer\nalwaysApply: false\n---\n\n" > "${CURSOR_DIR}/${SKILL_NAME}.mdc"
  cat "${SKILL_MD}" >> "${CURSOR_DIR}/${SKILL_NAME}.mdc"
  success "Cursor: ${CURSOR_DIR}/${SKILL_NAME}.mdc"
  INSTALLED=$((INSTALLED+1))
else
  skip "Cursor not found (${HOME}/.cursor missing)"
fi

# ── Step 5: Windsurf (.windsurf/rules/) ──────────────────────────────────────
WINDSURF_DIR="${HOME}/.windsurf/rules"
if [ -d "${HOME}/.windsurf" ]; then
  mkdir -p "${WINDSURF_DIR}"
  cp "${SKILL_MD}" "${WINDSURF_DIR}/${SKILL_NAME}.md"
  success "Windsurf: ${WINDSURF_DIR}/${SKILL_NAME}.md"
  INSTALLED=$((INSTALLED+1))
else
  skip "Windsurf not found (${HOME}/.windsurf missing)"
fi

# ── Step 6: Copilot / VS Code (.github/instructions/) ───────────────────────
VSCODE_DIR="${HOME}/.github/instructions"
if [ -d "${HOME}/.github" ]; then
  mkdir -p "${VSCODE_DIR}"
  cp "${SKILL_MD}" "${VSCODE_DIR}/${SKILL_NAME}.instructions.md"
  success "VS Code Copilot: ${VSCODE_DIR}/${SKILL_NAME}.instructions.md"
  INSTALLED=$((INSTALLED+1))
else
  skip "VS Code Copilot instructions dir not found (${HOME}/.github missing)"
fi

# ── Step 7: Check onchainos ──────────────────────────────────────────────────
printf "\n"
if command -v onchainos >/dev/null 2>&1; then
  ONCHAINOS_VER=$(onchainos --version 2>/dev/null || echo "unknown")
  success "onchainos CLI is installed (${ONCHAINOS_VER})"
else
  warn "onchainos CLI not found — required to mint."
  printf "\n  Install it:\n"
  printf "  ${CYAN}curl -sSL \"\$(curl -sSL https://api.github.com/repos/okx/onchainos-skills/releases/latest | grep -o 'https://raw.githubusercontent.com[^\"]*install.sh')\" | sh${NC}\n\n"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
printf "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  Installed to ${INSTALLED} agent runtime(s)${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n\n"

printf "  ${BOLD}Supported agents:${NC}\n"
printf "  • Claude Code  — say ${CYAN}\"mint my AgenticNFT\"${NC}\n"
printf "  • OpenClaw     — say ${CYAN}\"mint my Club of Agent NFT\"${NC}\n"
printf "  • Cursor       — ask ${CYAN}\"mint my Club of Agent NFT\"${NC}\n"
printf "  • Windsurf     — ask ${CYAN}\"mint my Club of Agent NFT\"${NC}\n"
printf "  • Any agent    — load ${CYAN}~/.agent-skills/${SKILL_NAME}/SKILL.md${NC}\n\n"
printf "  ${BOLD}For other agents (ChatGPT, Gemini, etc.):${NC}\n"
printf "  Paste the skill URL directly into your agent's context:\n"
printf "  ${CYAN}${GITHUB_RAW}${NC}\n\n"
printf "  Contract: ${CYAN}0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f${NC}\n"
printf "  Network:  X Layer Mainnet (chainId 196) · 0.08 OKB · gas-free\n\n"
