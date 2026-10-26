#!/usr/bin/env node
/**
 * MedOrqis CLI — Medical AI Skills Ecosystem
 * Zero-token clinical AI skills, safety guardrails & adapters.
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const command = (args[0] || '').toLowerCase();

const BANNER = `
\x1b[36m╔═══════════════════════════════════════════════════════════════════════╗\x1b[0m
\x1b[36m║\x1b[0m   \x1b[1m\x1b[32m✚ MedOrqis — Medical AI Skills Ecosystem (v2.1.1)\x1b[0m                 \x1b[36m║\x1b[0m
\x1b[36m║\x1b[0m   24 Specialized Skills · Zero-Token Core · Hardened Safety Gates     \x1b[36m║\x1b[0m
\x1b[36m║\x1b[0m   \x1b[90mWebsite:\x1b[0m https://seotarek.github.io/MedOrqis/                           \x1b[36m║\x1b[0m
\x1b[36m║\x1b[0m   \x1b[90mRepo:\x1b[0m    https://github.com/seotarek/MedOrqis                            \x1b[36m║\x1b[0m
\x1b[36m╚═══════════════════════════════════════════════════════════════════════╝\x1b[0m
`;

function getGroupedSkills() {
  const skillsShPath = path.join(ROOT_DIR, 'skills.sh.json');
  if (fs.existsSync(skillsShPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(skillsShPath, 'utf8'));
      return data.groupings || [];
    } catch (e) {}
  }
  return [];
}

function printStarFooter() {
  console.log('\x1b[90m─────────────────────────────────────────────────────────────────────────────\x1b[0m');
  console.log('\x1b[33m⭐ Support Open-Source Medical AI:\x1b[0m If MedOrqis helps your workflow, please star us on GitHub!');
  console.log('  \x1b[36m👉 https://github.com/seotarek/MedOrqis\x1b[0m\n');
}

switch (command) {
  case 'list': {
    console.log(BANNER);
    console.log('\x1b[1m\x1b[33mAvailable 24 Clinical AI Skills (Grouped by Specialty):\x1b[0m\n');
    const groupings = getGroupedSkills();
    let totalCount = 0;
    groupings.forEach((g, gIdx) => {
      console.log(`\x1b[1m\x1b[36m● Group ${gIdx + 1}: ${g.title}\x1b[0m`);
      console.log(`  \x1b[90m${g.description}\x1b[0m`);
      g.skills.forEach(skillName => {
        totalCount++;
        const num = String(totalCount).padStart(2, ' ');
        console.log(`    \x1b[32m${num}.\x1b[0m \x1b[1m${skillName}\x1b[0m`);
      });
      console.log('');
    });
    console.log(`\x1b[1mTotal Skills: ${totalCount}\x1b[0m\n`);
    console.log('\x1b[36mInstall any individual skill:\x1b[0m');
    console.log('  npx skills add seotarek/MedOrqis --skill <skill-name>\n');
    console.log('\x1b[36mInstall entire 24-skill ecosystem:\x1b[0m');
    console.log('  npx skills add seotarek/MedOrqis\n');
    printStarFooter();
    break;
  }

  case 'prompt': {
    console.log(BANNER);
    console.log('\x1b[1m\x1b[33mUniversal AI Prompt (Send to Claude, ChatGPT, Gemini, Cursor, Grok, etc.):\x1b[0m\n');
    console.log('\x1b[90m─────────────────────────────────────────────────────────────────────────────\x1b[0m');
    console.log(`You are operating with the MedOrqis Medical AI Skills Ecosystem (v2.1.1).
Repository: https://github.com/seotarek/MedOrqis
Web Showcase: https://seotarek.github.io/MedOrqis/

Instructions:
1. Review the 24 clinical skills catalog in SKILLS.md and skills.sh.json.
2. For clinical scores (CHA2DS2-VA ESC 2024, CKD-EPI 2021, Cockcroft-Gault, Wells DVT/PE, Bedside Schwartz, CURB-65), do NOT invent arithmetic. Rely strictly on deterministic formulas.
3. Enforce Epistemic Provenance: NEVER generate medication dosing or therapeutic plans on diagnoses tagged as MODEL_INFERRED_HYPOTHESIS without documented clinical record sign-off.
4. Missing Age Gatekeeper: If patient age is unrecorded, do NOT assume a default adult age (30); immediately flag SAFE_ABSTENTION_DATA_DEFICIT.
5. Identify sentinel red flags (Acute Stroke FAST, ACS crushing chest pain, Anaphylaxis, Sepsis, Anticoagulation + Bleeding) and escalate to emergency care immediately.`);
    console.log('\x1b[90m─────────────────────────────────────────────────────────────────────────────\x1b[0m\n');
    console.log('\x1b[32m✓ Copy the prompt above and send it to any LLM alongside the repository URL.\x1b[0m\n');
    printStarFooter();
    break;
  }

  case 'mcp': {
    console.log(BANNER);
    console.log('\x1b[1m\x1b[33mModel Context Protocol (MCP) Configuration:\x1b[0m\n');
    console.log('Add this block to your \x1b[1mclaude_desktop_config.json\x1b[0m or Cursor MCP settings:\n');
    const mcpConfig = {
      mcpServers: {
        medorqis: {
          command: "python3",
          args: [path.join(ROOT_DIR, "mcp_server", "medorqis_mcp_server.py")]
        }
      }
    };
    console.log(JSON.stringify(mcpConfig, null, 2));
    console.log('\n\x1b[32mExposes 5 live deterministic tools: calculate_clinical_score, check_red_flags, verify_evidence, scrub_phi, normalize_terminology.\x1b[0m\n');
    printStarFooter();
    break;
  }

  case 'help':
  default: {
    console.log(BANNER);
    console.log('\x1b[1mCommands:\x1b[0m');
    console.log('  \x1b[36mnpx medorqis list\x1b[0m      List all 24 risk-tiered clinical AI skills');
    console.log('  \x1b[36mnpx medorqis prompt\x1b[0m    Generate universal prompt to give to ANY AI model');
    console.log('  \x1b[36mnpx medorqis mcp\x1b[0m       Show MCP server stdio configuration');
    console.log('  \x1b[36mnpx medorqis help\x1b[0m      Display this help message\n');
    console.log('\x1b[1mInstall Skills into your Agent:\x1b[0m');
    console.log('  \x1b[32mnpx skills add seotarek/MedOrqis\x1b[0m                   \x1b[90m# Install full suite\x1b[0m');
    console.log('  \x1b[32mnpx skills add seotarek/MedOrqis --skill <name>\x1b[0m    \x1b[90m# Install single skill\x1b[0m\n');
    console.log('\x1b[1mInteractive Web Portal & Calculators:\x1b[0m');
    console.log('  \x1b[4mhttps://seotarek.github.io/MedOrqis/\x1b[0m\n');
    printStarFooter();
    break;
  }
}
