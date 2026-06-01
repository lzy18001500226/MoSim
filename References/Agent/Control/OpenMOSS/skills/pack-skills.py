"""
一键打包各角色 Skill 压缩包
每个 zip 包含: SKILL.md + task-cli.py

用法: python skills/pack-skills.py
输出: skills/dist/ 目录下生成各角色的 zip 文件
"""
import os
import zipfile
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(SCRIPT_DIR, "dist")
CLI_FILE = os.path.join(SCRIPT_DIR, "task-cli.py")

# 角色 Skill 目录列表
SKILL_DIRS = [
    "task-planner-skill",
    "task-executor-skill",
    "task-reviewer-skill",
    "task-patrol-skill",
]


def pack_skill(skill_dir_name):
    """打包单个角色的 Skill"""
    skill_path = os.path.join(SCRIPT_DIR, skill_dir_name)
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        print(f"  ⚠️  跳过 {skill_dir_name}: SKILL.md 不存在")
        return None

    zip_name = f"{skill_dir_name}.zip"
    zip_path = os.path.join(DIST_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 添加 SKILL.md（放在 skill 目录名下）
        zf.write(skill_md, os.path.join(skill_dir_name, "SKILL.md"))

        # 添加 task-cli.py（放在 skill 目录名下）
        zf.write(CLI_FILE, os.path.join(skill_dir_name, "task-cli.py"))

        # 如果 skill 目录下有其他文件也一并打包
        for root, dirs, files in os.walk(skill_path):
            for f in files:
                if f == "SKILL.md":
                    continue  # 已添加
                file_path = os.path.join(root, f)
                arcname = os.path.join(
                    skill_dir_name,
                    os.path.relpath(file_path, skill_path),
                )
                zf.write(file_path, arcname)

    return zip_path


def main():
    # 清理并创建 dist 目录
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)

    print("📦 开始打包 Skill 压缩包...\n")

    for skill_dir in SKILL_DIRS:
        result = pack_skill(skill_dir)
        if result:
            size_kb = os.path.getsize(result) / 1024
            print(f"  ✅ {skill_dir}.zip ({size_kb:.1f} KB)")

    print(f"\n📁 输出目录: {DIST_DIR}")
    print("🎉 打包完成！")


if __name__ == "__main__":
    main()
