import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const checklist = fs.readFileSync(path.join(repoRoot, 'docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html'), 'utf8');

test('P0受入チェックは再受入JPEGをサムネイルと拡大表示で提供する', () => {
  assert.match(checklist, /class="reacceptance-gallery"/);
  assert.match(checklist, /data-lightbox-open/);
  assert.match(checklist, /id="lightbox"/);
  assert.match(checklist, /data-lightbox-image/);
  assert.match(checklist, /project-dashboard01-before\.jpg/);
  assert.match(checklist, /project-dashboard01-after\.jpg/);
});
