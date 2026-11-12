from pathlib import Path


project_root = Path(SPECPATH).resolve()

a = Analysis(
    [str(project_root / "run_game.py")],
    pathex=[str(project_root / "src")],
    datas=[
        (str(project_root / "src/alien_invasion/images"), "alien_invasion/images"),
        (str(project_root / "src/alien_invasion/sounds"), "alien_invasion/sounds"),
    ],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AlienInvasion",
    console=False,
    upx=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="AlienInvasion",
    upx=False,
)
