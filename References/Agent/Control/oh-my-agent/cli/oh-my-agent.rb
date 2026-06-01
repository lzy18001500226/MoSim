class OhMyAgent < Formula
  desc "Portable multi-agent harness for .agents-based skills and workflows"
  homepage "https://github.com/first-fluke/oh-my-agent"
  url "https://registry.npmjs.org/oh-my-agent/-/oh-my-agent-7.16.0.tgz"
  sha256 "32826cb38a1d77e7f8ad3b892817bcaa78a6d1757a9a864e05a9f289b759040f"
  license "MIT"

  bottle do
    sha256 cellar: :any,                 arm64_tahoe:   "e5d252ad646fb58d6a723bd198d55279466393d7d5fa853838b01cf740468456"
    sha256 cellar: :any,                 arm64_sequoia: "8edf8246e068fd4a8963746db230bb31d892aed70b20f9cdff8fb06a714c1b15"
    sha256 cellar: :any,                 arm64_sonoma:  "8edf8246e068fd4a8963746db230bb31d892aed70b20f9cdff8fb06a714c1b15"
    sha256 cellar: :any,                 sonoma:        "0317c90a38215d3192b25b4f677fd6f8610d84cfef0de64a4308574d74963ef8"
    sha256 cellar: :any_skip_relocation, arm64_linux:   "88b9940620028ea72425701e851600b1fb1ea97595e632fa6032d4b6e7637945"
    sha256 cellar: :any_skip_relocation, x86_64_linux:  "16b48700cb8edfb85441b7700812ca776682d60bafd1519d70e7e91f22e98040"
  end

  depends_on "node"

  def install
    system "npm", "install", *std_npm_args

    node_modules = libexec/"lib/node_modules/oh-my-agent/node_modules"
    # Remove incompatible pre-built `bare-fs`/`bare-os`/`bare-url` binaries
    os = OS.kernel_name.downcase
    arch = Hardware::CPU.intel? ? "x64" : Hardware::CPU.arch.to_s
    node_modules.glob("{bare-fs,bare-os,bare-url}/prebuilds/*")
                .each { |dir| rm_r(dir) if dir.basename.to_s != "#{os}-#{arch}" }

    bin.install_symlink Dir[libexec/"bin/*"]
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/oh-my-agent --version")

    output = JSON.parse(shell_output("#{bin}/oh-my-agent memory:init --json"))
    assert_empty output["updated"]
    assert_path_exists testpath/".serena/memories/orchestrator-session.md"
    assert_path_exists testpath/".serena/memories/task-board.md"
  end
end
