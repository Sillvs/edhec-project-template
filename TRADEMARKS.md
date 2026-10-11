# Trademarks

The [MIT licence](LICENSE) covers the code, the stylesheets, the templates and
the documentation in this repository.

A copyright licence grants copyright rights. It does not grant trademark rights,
and MIT does not purport to. This page says out loud what that means here, so
nobody has to work it out from first principles.

## The EDHEC mark

`design/edhec-logo.svg` is EDHEC Business School's trademark, obtained from
`edhec.edu/sites/default/files/logo.svg`. It is included here, and embedded as a
data URI in every template, so that members of EDHEC can produce EDHEC-branded
coursework. **It is not ours to relicense**, and the MIT grant does not extend
to it.

The same goes for the name "EDHEC", the wordmark, and the burgundy as part of
the school's visual identity.

## If you are not at EDHEC and you fork this

Two edits and the whole thing is yours under MIT:

1. Replace `design/edhec-logo.svg` with your own mark, then run
   `python3 tools/inline_assets.py` so every template picks it up.
2. Change the burgundy `#5F1937` in `design/tokens.css` and run
   `python3 tools/sync_components.py`, which writes every token from that file
   into all four templates.

Then `./build.sh`. If it passes, the rebrand is complete; the build fails if a
template still disagrees with `design/tokens.css`.

These two steps were documented before they worked. `sync_components.py` only
ever wrote the component block, so the colour stayed behind in five files and
the next build failed with no hint as to why. Fixed, and verified by running
the instruction as written.

Using the EDHEC mark on work that is not EDHEC's is a trademark matter, not a
licence matter, and nothing in this repository permits it.

Whatever mark you substitute in, check what your own school or employer allows
before you publish. Most institutions have a brand policy, and most of them say
something about coursework.

## The example deck

`examples/auditcert-france-2026/` is a finished piece of coursework, kept as a
worked example. "AuditCert France" is a fictionalised client name from the
original case brief. Everyone in it other than the repository owner is referred
to by role rather than by name.
