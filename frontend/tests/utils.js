import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { JSDOM } from "jsdom";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function loadHTML(filename) {
    const html = fs.readFileSync(
        path.resolve(__dirname, `../../frontend/src/templates/${filename}`),
        "utf8"
    );
    const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable"});
    global.document = dom.window.document;
    global.window = dom.window;
    return dom;
}