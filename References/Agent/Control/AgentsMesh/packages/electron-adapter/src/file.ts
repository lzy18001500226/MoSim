import { invoke } from "./invoke";
import type { IFileService } from "@agentsmesh/service-interface";

export class ElectronFileService implements IFileService {
  async presign_upload(json: string): Promise<string> {
    return invoke<string>("filePresignUpload", json);
  }

  async upload_file(fileData: Uint8Array, filename: string, contentType: string): Promise<string> {
    return invoke<string>("fileUploadFile", Array.from(fileData), filename, contentType);
  }
}
