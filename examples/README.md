# Examples

## demo-tree-service
A complete reference site project for a **fictional** market ("Demo City, OK"). Use it to:
- see the content file format (front matter, shortcodes, FAQ sections) the `local-copywriter` follows
- see what the build produces (`python3 scripts/build_site.py examples/demo-tree-service`, then
  `python3 -m http.server -d examples/demo-tree-service/dist 8000`)
- test the QA gate (`python3 scripts/qa_site.py examples/demo-tree-service`)

It is deliberately short, and some pages carry "DEMO NOTE" boxes, so QA reports **thin-content warnings**, which is
expected here. In a real project every page meets the content-engine word targets with verified local substance.
`--launch` fails on purpose: the demo is `staging: true` and uses a fictional 555-01xx number and a `.invalid` domain.
