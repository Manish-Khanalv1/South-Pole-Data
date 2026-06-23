FEASABILITY ANALYSIS OF THE USE OF SOLAR PHOTOVOLTAICS TO POWER ICECUBE-GEN2 DRILLING AND OPERATIONS

    This code is to ananlyze and predict power output data from solar panels placed at the south pole


DESCRIPTION

    The University of Utah IceCube group has put 2 bifacial solar photovoltaic panels at the South Pole to understand the feasability of usang a large array of these panels to partially power future IceCube-Gen2 operations.
We were specifically interested in the nontrivial gain from the upwelling irradiance due to the high albedo snow present at the South Pole

    We can cross reference our data with Solar irradaince data from the National Oceanic and Atmospheric Administration (NOAA). These data were collected at the South Pole -along side our data- as part of the NOAA Global Monitoring Laboratory (GML)

    Many scripts espicially in the Analysis/Models/ directory are dedicated to making and perfecting models for both vertical and horizontal solar panels.

HOUSEKEEPING

    * Our data that we took with our panels at the pole are in a folder in the root called DataFolder. 
    * Device 101 is the first panel
    * Device 103 is the second panel and has a shaded area so we really only focused on device 101 to aid us in the simulation
    * Variables like power_101 or power_103 are the real power data we took 
    * We actually took voltage and current data and multiplied them together to get said power data
    * There was a problem with the DAQ script and in the data files we took:
        1. What is labeled as 'Device ID' is actually voltage
        2. What is labeled as 'Voltage' is actually current
        ergo: Whenever we use these data, we quickly reassign these when importing.
    * The NOAA Data are located on https://gml.noaa.gov/aftp/data/radiation/baseline/spo/ 
    * The array that gets imported when we import the data from this website needs to be spliced to get the specific data we care about
    * The imported NOAA array has a lot of information but we need:
        1. Time data
        2. Direct Irradiance
        3. Diffuse Irradaince
        4. Upwelling Irradiance
        5. Solar Zenith angle
    * NOAA Data were taken every minute, so there are 1440 of them
    * Our power output data were taken every 30s so there are 2880 of them

CODE AND LIBRARIES

    This project uses a mix of python files (.py) and jupyter notebooks (.ipynb)

    Python libraries used:

    numpy
    matplotlib
    pandas
    scipy
    seaborn
    LMfit

NOMENCLATURE

    Irradiances:
        1. Direct [dir]
        2. Diffuse [diff]
        3. Upwelling [up]
        (See Talks)
        4. Isotropic [iso]
            - usually Diffuse and Upwelling
    Efficiency = Conversion Factor
        - Conversion Factor is the best terminology to use when being official
        - efficiency or eff is often used on the code, but they are really interchangable for us

