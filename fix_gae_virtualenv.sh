#!/bin/sh

VENDORED_LIBS="$(pwd)/lib"

if [[ ! -d "$VENDORED_LIBS" ]]; then
    echo "Not in project root. Directory 'lib' not found." 1>&2
    exit 1
fi

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Not running in virtualenv." 1>&2
    exit 1
fi

PYTHON_CFG_HOOK="$VIRTUAL_ENV/lib/python2.7/site-packages/gae.pth"
APP_ENGINE_LIBS="$(gcloud info --format="value(installation.sdk_root)")/platform/google_appengine"

cat <<EOF >$PYTHON_CFG_HOOK
$APP_ENGINE_LIBS
$VENDORED_LIBS
import dev_appserver; dev_appserver.fix_sys_path()
EOF

echo "Python configuration hook for Google App Engine SDK created at '$PYTHON_CFG_HOOK'."