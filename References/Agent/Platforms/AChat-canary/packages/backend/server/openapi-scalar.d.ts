import "openapi-types";

declare module "openapi-types" {
  namespace OpenAPIV3 {
    interface Document {
      "x-tagGroups"?: Array<{
        name: string;
        tags: string[];
      }>;
    }
    interface TagObject {
      "x-displayName"?: string;
    }
  }
}
