class Codep < Formula
  desc "Instant macOS Spotlight & CLI launcher for your code projects"
  homepage "https://github.com/heliopais/codep"
  url "https://github.com/heliopais/codep/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # Updated on release tag
  license "MIT"
  head "https://github.com/heliopais/codep.git", branch: "main"

  depends_on :macos

  def install
    libexec.install "src/resolver.py"
    libexec.install "src/launcher.applescript"
    bin.install "bin/codep"
  end

  def caveats
    <<~EOS
      To enable the native Spotlight launcher (Cmd + Space -> codep):
        codep setup

      This compiles codep.app with native focus bypass into ~/Applications.
    EOS
  end

  test do
    assert_match "codep", shell_output("#{bin}/codep --help")
  end
end
