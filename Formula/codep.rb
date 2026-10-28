class Codep < Formula
  desc "Instant macOS Spotlight & CLI launcher for your code projects"
  homepage "https://github.com/heliopais/codep"
  url "https://github.com/heliopais/codep/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "976af663610c854631e7ad28eb39e68ba72483ff5e745e3ae768ba203e259155"
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
