cask "codep" do
  version "0.1.0"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # Updated on release tag

  url "https://github.com/heliopais/codep/releases/download/v#{version}/codep-#{version}.tar.gz"
  name "codep"
  desc "Instant macOS Spotlight & CLI project opener"
  homepage "https://github.com/heliopais/codep"

  depends_on macos: :monterey

  app "codep.app"
  binary "codep"

  caveats <<~EOS
    codep.app has been installed into /Applications.
    Hit Cmd + Space and type 'codep' to launch.
  EOS
end
