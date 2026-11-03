import test from "node:test";
import assert from "node:assert/strict";
import { buildScenePlan, classifyScene, makeTitle, splitNarration } from "../src/scene-planner.js";

test("splits narration at sentence endings and paragraph breaks", () => {
  const result = splitNarration("First sentence. Second sentence!\nA new paragraph?");
  assert.deepEqual(result, ["First sentence.", "Second sentence!", "A new paragraph?"]);
});

test("prioritizes cosmic imagery over a generic night reference", () => {
  assert.equal(classifyScene("The night sky is filled with distant stars.").visual, "space");
});

test("recognizes fear as a night scene with a worried expression", () => {
  assert.deepEqual(classifyScene("She is afraid of the darkness."), {
    visual: "night", mood: "worried", duration: 4
  });
});

test("recognizes time and conversation scenes", () => {
  assert.equal(classifyScene("A clock measures every second.").visual, "clock");
  assert.equal(classifyScene("Two friends discuss the discovery.").visual, "conversation");
});

test("keeps estimated scene duration within the preview limits", () => {
  const short = classifyScene("Hello.");
  const long = classifyScene("word ".repeat(1000));
  assert.equal(short.duration, 4);
  assert.equal(long.duration, 9);
});

test("builds sequential scene IDs and useful titles", () => {
  const plan = buildScenePlan("A curious mind asks why. The universe keeps expanding.");
  assert.equal(plan.length, 2);
  assert.deepEqual(plan.map((scene) => scene.id), [1, 2]);
  assert.equal(plan[0].visual, "science");
  assert.equal(plan[1].visual, "space");
  assert.equal(makeTitle("A small idea becomes a much larger story."), "A small idea becomes a much larger");
});
