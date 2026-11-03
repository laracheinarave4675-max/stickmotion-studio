import test from "node:test";
import assert from "node:assert/strict";
import { buildScenePlan, classifyScene, makeTitle, splitNarration } from "../src/scene-planner.js";

test("splits narration into sentence and paragraph beats", () => {
  assert.deepEqual(splitNarration("First sentence. Second sentence!\nA new paragraph?"), ["First sentence.", "Second sentence!", "A new paragraph?"]);
});
test("recognizes history and ancient civilizations", () => {
  assert.equal(classifyScene("The Roman empire expanded across Europe.").visual, "historical");
});
test("recognizes crime and investigation separately", () => {
  assert.equal(classifyScene("The detective found a fingerprint beside the body.").visual, "crime");
  assert.equal(classifyScene("Police questioned the witness about the case.").visual, "investigation");
});
test("recognizes survival environments", () => {
  assert.equal(classifyScene("He was stranded in the Sahara with no water.").visual, "survival");
  assert.equal(classifyScene("A sailor survived a shipwreck in the ocean.").visual, "shipwreck");
  assert.equal(classifyScene("A wolf followed him through the forest.").visual, "wilderness");
});
test("recognizes war, disaster and prison", () => {
  assert.equal(classifyScene("The soldiers prepared for battle.").visual, "war");
  assert.equal(classifyScene("An earthquake destroyed the town.").visual, "disaster");
  assert.equal(classifyScene("The prisoner planned an escape from his cell.").visual, "prison");
});
test("recognizes mood and clamps scene duration", () => {
  assert.equal(classifyScene("She was terrified and afraid.").mood, "worried");
  assert.equal(classifyScene("word ".repeat(1000)).duration, 9);
  assert.equal(classifyScene("Hello.").duration, 4);
});
test("builds ordered scenes and concise titles", () => {
  const plan = buildScenePlan("A curious mind asks why. The universe keeps expanding.");
  assert.deepEqual(plan.map((scene) => scene.id), [1, 2]);
  assert.equal(plan[0].visual, "science");
  assert.equal(plan[1].visual, "room");
  assert.equal(makeTitle("A small idea becomes a much larger story."), "A small idea becomes a much larger");
});
