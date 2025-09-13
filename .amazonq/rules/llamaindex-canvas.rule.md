# LlamaIndex Canvas Frontend

## Purpose
This rule defines how to implement the frontend using LlamaIndex Chat UI and Canvas components for multimedia artifact rendering.

## Instructions
- MUST use `@llamaindex/chat-ui` components for all chat interface elements (ID: LLAMAINDEX_CHAT_UI)
- MUST use `@llamaindex/canvas` for all artifact rendering (ID: LLAMAINDEX_CANVAS)
- ALWAYS follow the official Canvas demo implementation: https://github.com/run-llama/chat-ui/tree/7d36f0f2f80f92977fba331b85d5e2f74691877e/apps/web/app/demo/canvas (ID: CANVAS_DEMO_REFERENCE)
- MUST handle LlamaIndex message format with parts array: `messages[].parts[].text` (ID: LLAMAINDEX_MESSAGE_FORMAT)
- ALWAYS implement Canvas provider at application root level (ID: CANVAS_PROVIDER_ROOT)
- MUST support all artifact types: chart, image, document, table, video, audio, url, map (ID: ALL_ARTIFACT_TYPES)
- When creating artifacts, ALWAYS ensure they are responsive and accessible (ID: RESPONSIVE_ACCESSIBLE)
- MUST use MapLibre GL JS for map artifacts consuming py-maplibregl specifications (ID: MAPLIBRE_MAPS)
- ALWAYS use TypeScript with strict mode enabled (ID: TYPESCRIPT_STRICT)

## Priority
High

## Error Handling
- If Canvas components fail to render, fall back to text-only display and log the error
- If artifact data is malformed, display error message and continue with text response
- If MapLibre fails to load, show static map placeholder with coordinates
