import subprocess

APPLESCRIPT = """
tell application "Mail"
    set output to ""
    set alleMailboxen to every mailbox of every account
    repeat with mailboxLijst in alleMailboxen
        repeat with mb in mailboxLijst
            set ongelezen to (messages of mb whose read status is false)
            repeat with bericht in ongelezen
                set afzender to sender of bericht
                set onderwerp to subject of bericht
                set datum to date received of bericht
                set output to output & afzender & "||" & onderwerp & "||" & (datum as string) & "\n"
            end repeat
        end repeat
    end repeat
    return output
end tell
"""

resultaat = subprocess.run(
    ["osascript", "-e", APPLESCRIPT],
    capture_output=True,
    text=True
)

if resultaat.returncode != 0:
    print("Fout bij het uitlezen van Apple Mail:")
    print(resultaat.stderr)
else:
    regels = [r for r in resultaat.stdout.strip().split("\n") if r]

    if not regels:
        print("Geen ongelezen e-mails gevonden.")
    else:
        print(f"{len(regels)} ongelezen e-mail(s):\n")
        print(f"{'Nr.':<4} {'Afzender':<35} {'Onderwerp':<45} {'Datum'}")
        print("-" * 100)
        for i, regel in enumerate(regels, start=1):
            delen = regel.split("||")
            if len(delen) == 3:
                afzender, onderwerp, datum = delen
                print(f"{i:<4} {afzender[:33]:<35} {onderwerp[:43]:<45} {datum}")
