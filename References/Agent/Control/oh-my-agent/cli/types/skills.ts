export interface SkillInfo {
  name: string;
  desc: string;
}

export interface SkillsRegistry {
  domain: SkillInfo[];
  design: SkillInfo[];
  coordination: SkillInfo[];
  utility: SkillInfo[];
  infrastructure: SkillInfo[];
}

export interface SkillCheck {
  name: string;
  installed: boolean;
  hasSkillMd: boolean;
}
