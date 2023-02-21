# This is the Service Request System that is deployed on AWS Openshift.  

The openshift project is here:
https://containers.it.umich.edu/console/project/srs/overview

#  The project serves three environments:

dev:
https://srs-dev.dsc.umich.edu/
Environment setting are in the [dev config map](https://containers.it.umich.edu/console/project/srs/browse/config-maps/dev).
Changes to the development branch will trigger a rebuild of the dev deployment.

qa:
https://srs-qa.dsc.umich.edu/
Environment setting are in the [qa config map](https://containers.it.umich.edu/console/project/srs/browse/config-maps/qa).
Changes to the qa branch require a redeploy of the QA pod.

production:
https://srs.it.umich.edu/
Environment setting are in the [production config map](https://containers.it.umich.edu/console/project/srs/browse/config-maps/production).
This is built from the master branch.  Rebuilds are manual.

Admins can access an openshift "cheat sheet" [here](https://docs.google.com/document/d/1FrGvyXhpybbMKpLENfLhjxzAmKt60gbj2Tz9A6PlUjk/edit).

Lorem
