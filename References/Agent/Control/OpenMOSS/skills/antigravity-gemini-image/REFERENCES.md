# Antigravity Gemini Image — Quick Reference

- Model: `gemini-3.1-flash-image`
- Endpoint (via gateway): `POST {BASE_URL}/v1beta/models/{model}:generateContent`
- Auth header: `x-goog-api-key: <key>`
- Request body:
  - `contents`: list of `{role, parts}`
  - `parts`: text prompt + optional `inlineData` (image)
  - `generationConfig`: e.g. `temperature`
- Output image:
  - `candidates[0].content.parts[*].inlineData.data` (base64)

Notes:
- This model does **not** work reliably with `/v1/responses` + `image_generation` in our gateway.
- Use the Gemini REST format shown above.
