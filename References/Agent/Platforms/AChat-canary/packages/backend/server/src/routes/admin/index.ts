import { Hono } from "hono";

import model from "./model";

const app = new Hono()
  .route("/", model);

export default app;
