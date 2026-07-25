#!/usr/bin/env node
//
// setup/install.mjs — claude-stack.json 하나만 읽고 이 PC의 Claude Code 환경을 재현한다.
//
//   node setup/install.mjs             실제 설치 (pinnedCommits 에 고정된 버전)
//   node setup/install.mjs --dry-run   무엇을 할지만 출력 (아무것도 바꾸지 않음)
//   node setup/install.mjs --latest    고정 커밋 무시하고 각 저장소 최신으로
//   node setup/install.mjs --skills    스킬만
//   node setup/install.mjs --plugins   플러그인만
//   node setup/install.mjs --mcp       MCP 서버만
//
// 원칙 — 기존 것을 절대 조용히 덮어쓰지 않는다.
//   없으면            → 설치
//   내용이 같으면      → 건너뜀
//   내용이 다르면      → <이름>.bak-<타임스탬프> 로 백업한 뒤 업데이트
//
// 의존성 없음. Node 18+ 와 git, (플러그인·MCP 단계에서) claude CLI 만 있으면 된다.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..');
const MANIFEST = JSON.parse(fs.readFileSync(path.join(HERE, 'claude-stack.json'), 'utf8'));

const argv = process.argv.slice(2);
const DRY = argv.includes('--dry-run');
const LATEST = argv.includes('--latest');
const only = ['--skills', '--plugins', '--mcp'].filter((f) => argv.includes(f));
const want = (kind) => only.length === 0 || only.includes(`--${kind}`);

const CLAUDE_DIR = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const SKILLS_DIR = path.join(CLAUDE_DIR, 'skills');

// ---------------------------------------------------------------- 출력 헬퍼
const C = { dim: '\x1b[2m', b: '\x1b[1m', g: '\x1b[32m', y: '\x1b[33m', r: '\x1b[31m', c: '\x1b[36m', x: '\x1b[0m' };
const step = (m) => console.log(`\n${C.c}==>${C.x} ${C.b}${m}${C.x}`);
const log = (icon, name, msg = '') => console.log(`    ${icon} ${name.padEnd(26)} ${C.dim}${msg}${C.x}`);
const results = [];
const record = (kind, name, action, detail = '', backup = null) => {
  results.push({ kind, name, action, detail, backup });
  const icon = { 설치: `${C.g}+${C.x}`, 업데이트: `${C.y}↑${C.x}`, 건너뜀: `${C.dim}·${C.x}`, 실패: `${C.r}✗${C.x}` }[action];
  log(icon, name, detail || action);
};

// ---------------------------------------------------------------- 파일 헬퍼
const exists = (p) => fs.existsSync(p);

function walk(dir, base = dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === '.git') continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full, base, out);
    else out.push(path.relative(base, full).split(path.sep).join('/'));
  }
  return out;
}

// 디렉터리 내용 해시 — 경로와 파일 내용을 모두 반영해 "같은지"를 판정한다.
function hashDir(dir) {
  if (!exists(dir)) return null;
  const h = crypto.createHash('sha256');
  for (const rel of walk(dir).sort()) {
    h.update(rel);
    h.update(fs.readFileSync(path.join(dir, rel)));
  }
  return h.digest('hex');
}

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const e of fs.readdirSync(from, { withFileTypes: true })) {
    if (e.name === '.git') continue;
    const s = path.join(from, e.name);
    const d = path.join(to, e.name);
    if (e.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

const stamp = () => new Date().toISOString().replace(/[-:T]/g, '').slice(0, 12);

// 핵심 정책: 없으면 설치 / 같으면 건너뜀 / 다르면 백업 후 업데이트
function installSkillDir(name, srcDir) {
  const dst = path.join(SKILLS_DIR, name);

  if (exists(dst)) {
    if (fs.lstatSync(dst).isSymbolicLink()) {
      return record('skill', name, '건너뜀', '심볼릭 링크가 이미 있음 — 다른 도구가 관리 중');
    }
    if (hashDir(dst) === hashDir(srcDir)) {
      return record('skill', name, '건너뜀', '내용 동일');
    }
    const bak = `${dst}.bak-${stamp()}`;
    if (DRY) return record('skill', name, '업데이트', `(dry-run) 기존 폴더를 ${path.basename(bak)} 로 백업 후 교체`);
    fs.renameSync(dst, bak);
    copyDir(srcDir, dst);
    return record('skill', name, '업데이트', `기존 폴더 → ${path.basename(bak)}`, bak);
  }

  if (DRY) return record('skill', name, '설치', '(dry-run)');
  copyDir(srcDir, dst);
  record('skill', name, '설치');
}

// ---------------------------------------------------------------- 명령 헬퍼
// Windows 의 claude/git 은 .cmd 셔임이라 shell 을 거쳐야 한다.
// 인자를 따로 넘기면 Node 가 DEP0190 경고를 내므로, 셸을 쓸 때는 한 문자열로 합쳐서 넘긴다.
// (여기서 쓰는 인자는 전부 이 파일 안의 고정 리터럴이라 주입 위험이 없다.)
function run(cmd, args, opts = {}) {
  if (process.platform === 'win32') {
    const line = [cmd, ...args].map((a) => (/[\s"]/.test(a) ? `"${a}"` : a)).join(' ');
    return spawnSync(line, { encoding: 'utf8', shell: true, ...opts });
  }
  return spawnSync(cmd, args, { encoding: 'utf8', ...opts });
}
const have = (cmd) => run(cmd, ['--version']).status === 0;

// ================================================================ 0. 사전 점검
step('사전 점검');
for (const c of ['git', 'node']) {
  if (!have(c)) { console.error(`${C.r}${c} 를 찾을 수 없습니다. 먼저 설치하세요.${C.x}`); process.exit(1); }
  log('✓', c);
}
const HAS_CLAUDE = have('claude');
if (!HAS_CLAUDE) log('!', 'claude CLI', '없음 — 플러그인/MCP 단계는 건너뜁니다');
log('·', 'skills 디렉터리', SKILLS_DIR);
if (DRY) console.log(`\n${C.y}[dry-run] 실제로는 아무것도 바꾸지 않습니다.${C.x}`);

fs.mkdirSync(SKILLS_DIR, { recursive: true });

// ================================================================ 1. 내장 스킬
if (want('skills')) {
  step('이 리포에 담긴 스킬');
  const repoIsSkillsDir = (() => {
    try { return fs.realpathSync(REPO) === fs.realpathSync(SKILLS_DIR); } catch { return false; }
  })();

  if (repoIsSkillsDir) {
    log('·', '(전체)', '이 리포가 곧 skills 디렉터리 — 이미 제자리에 있음');
  } else {
    for (const s of MANIFEST.vendoredSkills) {
      const src = path.join(REPO, s.name);
      if (!exists(src)) { record('skill', s.name, '실패', '리포에 폴더가 없음'); continue; }
      installSkillDir(s.name, src);
    }
  }

  // ============================================================== 2. 외부 스킬
  step('외부 저장소 스킬');
  const byRepo = new Map();
  for (const s of MANIFEST.externalSkills) {
    if (!byRepo.has(s.repo)) byRepo.set(s.repo, []);
    byRepo.get(s.repo).push(s);
  }

  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'claude-stack-'));
  try {
    for (const [repo, skills] of byRepo) {
      const pin = LATEST ? null : (MANIFEST.pinnedCommits || {})[repo];
      console.log(`  ${C.dim}${repo} ${pin ? `@ ${pin.slice(0, 7)}` : '@ latest'}${C.x}`);

      const clone = path.join(tmpRoot, repo.replace('/', '__'));
      const url = `https://github.com/${repo}.git`;
      let ok;

      if (pin) {
        // 고정 커밋을 받으려면 clone 대신 init + 특정 SHA fetch 를 써야 한다.
        fs.mkdirSync(clone, { recursive: true });
        ok =
          run('git', ['init', '-q'], { cwd: clone }).status === 0 &&
          run('git', ['remote', 'add', 'origin', url], { cwd: clone }).status === 0 &&
          run('git', ['fetch', '-q', '--depth', '1', 'origin', pin], { cwd: clone }).status === 0 &&
          run('git', ['checkout', '-q', 'FETCH_HEAD'], { cwd: clone }).status === 0;
        if (!ok) {
          console.log(`    ${C.y}!${C.x} 고정 커밋을 받지 못해 최신으로 대체합니다`);
          fs.rmSync(clone, { recursive: true, force: true });
          ok = run('git', ['clone', '-q', '--depth', '1', url, clone]).status === 0;
        }
      } else {
        ok = run('git', ['clone', '-q', '--depth', '1', url, clone]).status === 0;
      }

      if (!ok) {
        for (const s of skills) record('skill', s.name, '실패', `내려받기 실패: ${repo}`);
        continue;
      }
      for (const s of skills) {
        const src = s.path === '.' ? clone : path.join(clone, ...s.path.split('/'));
        if (!exists(src)) { record('skill', s.name, '실패', `경로 없음: ${s.path}`); continue; }
        installSkillDir(s.name, src);
      }
    }
  } finally {
    fs.rmSync(tmpRoot, { recursive: true, force: true });
  }
}

// ================================================================ 3. 플러그인
if (want('plugins') && HAS_CLAUDE) {
  step('플러그인 마켓플레이스');
  for (const m of MANIFEST.marketplaces) {
    if (DRY) { record('marketplace', m.name, '설치', '(dry-run)'); continue; }
    const r = run('claude', ['plugin', 'marketplace', 'add', m.repo]);
    record('marketplace', m.name, r.status === 0 ? '설치' : '건너뜀', r.status === 0 ? m.repo : '이미 등록됨 또는 실패');
  }

  step('플러그인');
  for (const p of MANIFEST.plugins) {
    if (DRY) { record('plugin', p.id, '설치', '(dry-run)'); continue; }
    const r = run('claude', ['plugin', 'install', p.id]);
    record('plugin', p.id, r.status === 0 ? '설치' : '건너뜀', r.status === 0 ? '' : '이미 설치됨 또는 실패');
  }
}

// ================================================================ 4. MCP 서버
if (want('mcp') && HAS_CLAUDE) {
  step('MCP 서버 (user 스코프)');
  const listed = run('claude', ['mcp', 'list']).stdout || '';
  for (const m of MANIFEST.mcpServers) {
    if (new RegExp(`^\\s*${m.name}:`, 'm').test(listed)) {
      record('mcp', m.name, '건너뜀', '이미 등록됨');
      continue;
    }
    if (DRY) { record('mcp', m.name, '설치', '(dry-run)'); continue; }
    const r = run('claude', ['mcp', 'add', m.name, '--scope', 'user', '--', ...m.command]);
    record('mcp', m.name, r.status === 0 ? '설치' : '실패', m.command.join(' '));
  }
}

// ================================================================ 5. 설정 파일
if (want('skills')) {
  step('설정 파일');
  const cavemanDir = process.env.XDG_CONFIG_HOME
    ? path.join(process.env.XDG_CONFIG_HOME, 'caveman')
    : process.platform === 'win32'
      ? path.join(process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'), 'caveman')
      : path.join(os.homedir(), '.config', 'caveman');
  const cavemanCfg = path.join(cavemanDir, 'config.json');

  if (exists(cavemanCfg)) {
    record('config', 'caveman/config.json', '건너뜀', '이미 존재 — defaultMode 를 직접 확인하세요');
  } else if (DRY) {
    record('config', 'caveman/config.json', '설치', '(dry-run) defaultMode: off');
  } else {
    fs.mkdirSync(cavemanDir, { recursive: true });
    fs.writeFileSync(cavemanCfg, JSON.stringify({ defaultMode: 'off' }, null, 2) + '\n');
    record('config', 'caveman/config.json', '설치', 'defaultMode: off');
  }
}

// ================================================================ 요약
step('요약');
const tally = results.reduce((a, r) => ((a[r.action] = (a[r.action] || 0) + 1), a), {});
console.log(`    설치 ${tally['설치'] || 0} · 업데이트 ${tally['업데이트'] || 0} · 건너뜀 ${tally['건너뜀'] || 0} · 실패 ${tally['실패'] || 0}`);

const failed = results.filter((r) => r.action === '실패');
if (failed.length) {
  console.log(`\n${C.r}실패 항목${C.x}`);
  for (const f of failed) console.log(`    ${f.name} — ${f.detail}`);
}

const backups = results.filter((r) => r.backup);
if (backups.length) {
  console.log(`\n${C.y}백업된 기존 폴더${C.x} (내용 확인 후 지우세요)`);
  for (const b of backups) console.log(`    ${b.backup}`);
}

console.log(`
${C.b}남은 수동 단계${C.x}
  1. NotebookLM 인증 — 대화형 claude 세션에서 setup_auth 실행 → Chrome 에서 Google 로그인 (PC당 1회)
  2. claude.ai 커넥터(Notion·Figma·Gamma 등)는 계정 단위라 로그인하면 따라옵니다
  3. ${C.b}Claude Code 재시작${C.x} — 새 스킬/플러그인은 재시작해야 로드됩니다
`);
