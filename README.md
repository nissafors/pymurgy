# Pymurgy library for brewing

Pymurgy is a library for beer recipe creation and brewing calculator type applications.

## Creating a recipe

From a recipe we expect a list of ingredients - water, extract givers, hops, yeast and adjuncts - plus amounts and some
important properties of these ingredients. We also expect some basic information about how to brew this specific beer,
like boil time, mash steps, fermentation temperatures and lagering.

The way you design a recipe with pymurgy is to instantiate objects for each ingredient. Extract, Hop, Yeast, Adjunct and
CO2 are dataclasses that has fields for ingredient amounts and properties, and methods to compute their contributions
to the recipes overall qualities. These objects are then used to instantiate a Recipe class, which also has fields for
a few recipe specific properties, and methods to compute the aggregated properties of ingredients and processes.

With a Recipe instance you can compute:
* Pre-boil volume
* Pre-boil gravity
* Original gravity
* Final gravity
* Alcohol content
* Bitternes
* Beer color
* Water ion content
