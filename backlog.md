
* performance and memory optimization
    * use python generators (yield)
    * flag for disabling bundles and resource cache?
    * flush method?
* bundle(s) to
    * csv
    * excel
* error handling
    * throwing exceptions
    * check todos
* add class FhirDataFrame
* set DataFrame index
* set DataFrame data types
* python naming
* python best practices
* linting
* unit testing
* documentation
* module creation (pip)

* additional features
    * datetime columns generation
    * anonymization?

* FHIR specifications support
    * should support all the values in codes
        * currently only first code is used e.g. from encounter code and reason code
        * is it possible to add multiple values to cell in pandas?
            * maybe not? use additional data frame
    * add also code system along with code values
        * currently SNOMED-CT code system expected

* applications
    * notebooks / posts (kaggle kernels, medium)
        * deep learning in healthcare: FHIR, FHIRpandas and fastai
        * exploring FHIR with FHIRpandas
            * FHIR-resources.ipynp
        * share in FHIR, fastai, kaggle communities
    * FHIR to csv & excel service
        * python serverless functions on AWS or GCP
        * front-end
            * upload FHIR JSONs
            - seacrh from public FHIR server  
            * bundle visualization (github-like commit activity)
            * display tables
            * download tables
* 
