$nodePath = "C:\Program Files\nodejs"

if (Test-Path "$nodePath\npm.cmd") {
    $env:Path = "$nodePath;$env:Path"
}

npm install
npm run dev
