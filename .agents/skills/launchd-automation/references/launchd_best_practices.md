# launchd lifecycle reference

Read this when a job misbehaves at load, at run, or after a change. Placement and
report-root rules live in `automation/README.md`. The workflow lives in `SKILL.md`.

## Domains

| Domain target | Typical location | Runs as |
| --- | --- | --- |
| `gui/<uid>` | `~/Library/LaunchAgents/` | The logged-in user, with keychain and display access |
| `system` | `/Library/LaunchDaemons/` | Root, with no user session |

User automation belongs in `gui/<uid>`. A daemon cannot reach the user keychain or
a mounted network home the way an agent can. Moving a job between domains changes
its environment more than its command.

## Modern launchctl

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist
launchctl bootout   gui/$(id -u)/<label>
launchctl print     gui/$(id -u)/<label>
launchctl kickstart gui/$(id -u)/<label>
```

`load` and `unload` are legacy. `bootstrap` reads the plist and registers it.
`bootout` by label removes the registration even when the plist file is gone.
`print` is read-only and is the safe inspection call.

`bootstrap` fails with `Bootstrap failed: 5: Input/output error` when the label is
already loaded in that domain. Boot out first, then bootstrap. A plist the domain
rejects, a missing executable, or unreadable permissions produce other failures;
read the message instead of retrying.

`kickstart` starts the job now. Its exit code 0 means the request was accepted,
not that the job ran, and never that the job finished. `kickstart -k` kills a
running instance first; use it only when an interruption is authorized.

## Absolute paths and environment

launchd starts a process with a minimal `PATH` (`/usr/bin:/bin:/usr/sbin:/sbin`),
no shell profile, no version manager, and no working directory guarantee.

- Give `ProgramArguments` an absolute executable path.
- Pass file arguments as absolute paths. A relative path resolves against a
  directory the plist did not choose.
- Declare `EnvironmentVariables` in the plist. That declaration is the job's
  environment.
- A wrapper is optional. Add one for a lock, a terminal event line, or shared
  setup. Do not add one to source `.env`, a shell profile, or `mise`/`pyenv`/`nvm`;
  those make the scheduled environment differ from the declared one.

## Scheduling and sleep

`StartCalendarInterval` fires at local wall-clock time. A time that passes while
the Mac sleeps fires when it wakes, once, late. A time skipped across a shutdown
does not replay. `StartInterval` counts from the previous start and does not
advance while asleep. Neither primitive retries a failed run.

`RunAtLoad` starts the job at bootstrap. It is off unless the job needs it; it is
not a verification step. `KeepAlive` restarts a service that exits; a scheduled
job that should exit normally does not want it.

Timezone: the plist stores no zone. The Mac's zone at fire time decides the
moment. A job whose correct time is fixed must convert in its own code and record
the zone it used.

## Logs and reports

`StandardOutPath` and `StandardErrorPath` capture the process streams. They are
append-only and never rotate. Point them at the report root, outside the source
folder. Structured run records, rotation, and `latest-result.json` belong to the
job; a wrapper that writes one terminal line per run makes a live check possible
without reading the whole log.

## Exit codes

| Code | Name | Usual cause |
| --- | --- | --- |
| `0` | success | The program finished normally. It says nothing about the intended effect. |
| `1` | general failure | The program raised an error. Read the stderr log. |
| `78` | `EX_CONFIG` | launchd rejected the configuration: bad plist, missing program, unusable path, or a refused bootstrap. |
| `126` | not executable | The program or wrapper lacks the executable bit, or the volume refuses execution. |
| `127` | command not found | The program path is wrong, or the program calls a tool absent from the declared `PATH`. |

`launchctl print` shows the last exit status under `last exit code`. A status from
an earlier run is stale evidence; match it to a run record before trusting it.

## Deploy sequence

1. Lint: `plutil -lint <source plist>`.
2. Compare the source and installed copies when both exist.
3. `launchctl bootout gui/$(id -u)/<label>` and tolerate "not loaded".
4. Copy the source plist to `~/Library/LaunchAgents/<label>.plist`.
5. `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist`.
6. Read `launchctl print` and confirm the loaded `path`.

Keep the previous plist before step 4. Rollback repeats the sequence with the
saved copy.

## Verification

Static checks read files and call `plutil -lint` and read-only `launchctl print`.
They never execute the job.

A live check may kickstart the loaded job, then waits for a fresh terminal
outcome: a `latest-result.json` with an `outcome`, or a `terminal=` line appended
to the log after the kickstart. Absence of a result is a failure, even when
dispatch succeeded. A `failed` outcome proves the job ran and did not succeed;
report it as failure, not as a completed check.

A runner cannot report its own absence. Detect a missed schedule with a separate
observer that reads the age of the latest result.
