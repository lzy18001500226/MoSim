export interface ManifestFile {
  path: string;
  sha256: string;
  size: number;
}

export interface Manifest {
  name: string;
  version: string;
  releaseDate: string;
  repository: string;
  files: ManifestFile[];
  checksums?: {
    algorithm: string;
  };
  metadata?: {
    skillCount: number;
    workflowCount: number;
    totalFiles: number;
  };
}
