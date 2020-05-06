# Interspeech-2020-Perceptimatic

This git contains the dataset Native Perceptimatic presented in the paper NAME PAPER, along with all the code to perform the analysis done in the latter.

### General environment required
* python 3.6/7
* numpy
* scipy
* pandas
* statsmodels

# Dataset
## Cleaned stimuli
[DESCRIPTION STIMULI FILE]

## Human test
We give all the code to perform the human experiments, and we provide the triplet used on demand (contact juliette.millet@cri-paris.org)

## Human results
[DESCRIPTION HUMAN RESULTS FILE]


# Analysis code
In this section we describe all the steps to evaluate any model with our methods.

## Extracting features from your model
First of all you need to extract the model you want to evaluate's representations of the 2017 ZeroSpeech one second stimuli. The original wavfiles can be downloaded here: https://download.zerospeech.com/. 

Our evaluation system requires that your system outputs a vector of feature values for each frame. For each utterance in the set (e.g. s2801a.wav), an ASCII features file with the same name (e.g. s2801a.fea) as the utterance should be generated with the following format (separator = ' '):

| | | | |
| --- | --- | --- | --- |
| time1  | val1  |  ...  | valN |
| time2 | val1 |    ... | valN |

example:

| | | | | | |
| --- | --- | --- | --- | --- | --- |
|0.0125 | 12.3 | 428.8 | -92.3 | 0.021 | 43.23 |
|0.0225 | 19.0 | 392.9 | -43.1 | 10.29 | 40.02 |

Note

The time is in seconds. It corresponds to the center of the frame of each feature. In this example, there are frames every 10ms and the first frame spans a duration of 25ms starting at the beginning of the file, hence, the first frame is centered at .0125 seconds and the second 10ms later. It is not required that the frames be regularly spaced.
  
## Extracting delta values from features

Once your features are in the right format, you need to put them in a global folder (called M here), put your English features in M/english/1s/, and your French features in M/french/1s. Then do:

`python script_get_file_distance.py M/ DATA/all_triplets.csv $file_delta.csv$ $distance$ DATA/english/all_aligned_clean_english.csv DATA/french/all_aligned_clean_french.csv False False`

If your features use the format h5f, replace the 'False False' at the end by 'True False'

`$file_delta.csv` is the file created by the script: it contains all the delta values for each triplet in DATA/all_triplets.csv.

`$distance$` can be 'euclidean', 'kl' or 'cosine': it is the distance you want to use for the DTW. This can adapted if your representations are not numerical.

The script also print the ABX error over the Native Perceptimatic dataset (for English and French).

In order to perform the rest of the analysis easily, you can add your model delta values to our existing file containing human results, and all the model we evaluated 's delta values. To do that you need to do:

`python concatenate_results $file_delta.csv$ $name_model$ DATA/humans_and_models.csv $file_all.csv$`

`$name_model$` if the name of the new column you add to the original file containing human results. You obtain a file (`$file_all.csv$`) containing all the data in humans_and_models.csv and the delta values you computed.

## Computing ABX accuracies

Once `$file_all.csv` is created, you can compute the normal ABX accuracies over the Native Perceptimatic dataset:

`python compute_results_unweighted.py $file_all.csv$ $name_model$`

It will print the ABX accuracy over the Perceptimatic dataset (for French and English).

You can also compute the reweighted by human results ABX accuracy:

`python compute_results_weighted_human.py $file_all.csv$ binarized_answer $name_model$`

It will print the reweighted by human results ABX accuracy (for French and English).
 
## Comparing humans' and models' results

In our paper, to compare human perceptual space and models' representational space, we study how well the delta values obtained by the models' features can predict individual human results. 
To do that we fit a probit regression per model using different input (see paper for details), and instead of doing it on all human results, we resample them multiple times 
(in order to obtain confidence intervals on the differences, see last section of this README). To do the same thing with your new model, and compare it to the models we used,
you need the $file_all.csv$ created above. Do:

`python probit_model_bootstrap.py $file_all.csv$ $file_log.csv$ $nb_it$`

$nb_it$ corresponds to the number of resampling you want to perform. $file_log.csv$ will contain one column per model (with a index column at the beginng), each row represents a sample.

To obtain average log-likelihoods along with 95% intervals do:

`python compute_log_interval.py $file_log.csv$ $final_average_log.csv`

$final_average_log.csv$ will contain one row per model, each row with the values: name of the model, average log-likeliood, min 95% interval, max 95% interval.

To obtain average log-likelihood **differences** along with 95% intervals, do:

`python compute_log_interval.py $file_log.csv$ $final_average_diff_log.csv`

$final_average_diff_log.csv$ will contain one row per couple of model, each row with the values: name of the model first, name of model second, average log-likelihood difference, min 95% interval, max 95% interval.

The log-likelihood difference is loglik(name of the model first) - loglik(name of the model second).


# Extracting features used in the paper
delta values obtained for the different models can be found in the file DATA/humans_and_models.csv, one column per model with the codenames given in the paper.
 But if you want to extract the features yourself in order to recompute the delta values, you can follow these instructions:

## ZeroSpeech 2017 models
The features used for the ZS2017 models are the ones submitted to the 2017 ZeroSpeech challenge. The latter can be found online, by clicking on Zenodo links that are listed here: https://zerospeech.com/2017/results.html

Here is a list of the models we evaluated, and their corresponding Zenodo number (we also precise if the downloaded features are already .fea, h5f or need to be modified)


Model | Zenodo number | type | distance used |
--- | --- | --- | --- |
S2 | 823695 | fea | cosine |
S1 | 815089 | fea | cosine |
H | 821246 | fea | kl |
P1 | 819892 | h5f | cosine |
P2 | 820409 | h5f | cosine |
A3 | 823546 | h5f | cosine |
Y1 | 814335 | need modif | cosine |
Y2 | 814579 | fea | cosine |
Y3 | 814566 | fea | cosine |
C1 | 822737 | fea | cosine |
C2 | 808915 | need modif | cosine |

## Topline
The topline used is a supervised GMM-HMM model with a bigram language model, trained with a Kaldi recipe. We used exactly the same model than for the 2017 Zerospeech challenge. 
We cannot provide the models themselves (one trained on the 2017 Zerospeech French training set, the other on the English training set), but we provide the posteriorgrams extracted on demand (contact juliette.millet@cri-paris.org)

## MFCCs
The MFCCs used in the paper were extracted with Kaldi toolkit, using the default paramters, adding the first and second derivatives for a total of 39 dimensions, and we applymean-variance normalization over a moving 300 milliseconds window. We provide the extracted MFCCs on demand on demand (contact juliette.millet@cri-paris.org)

## Multilingual bottleneck
We used the Shennong package (https://github.com/bootphon/shennong) to extract the multilingual botteneck features described in [CITE paper] 

To extract these features you need the Shennong package installed (added to the list of requirements listed above). To extract features from wavfiles in a folder F to a folder G do

`python extract_from_shennong_bottleneck.py F G BabelMulti`

## DPGMM

We use the kaldi toolkit to extract MFCCs and apply the same VTLN than in [CITE] (the vtln-mfccs can be provided on demand, contact juliette.millet@cri-paris.org), then we  extract the posteriorgrams from the French and English models from [CITE] we follow the instructions of https://github.com/geomphon/CogSci-2019-Unsupervised-speech-and-human-perception

# Other notes
## Details results of the sampling
To study how well each model is able to predict human results, we fit a probit model using delta values and a set of other parameters on human results for each model. Instead of doing it on all human results,
 we do it on mutliple subsamples (N=13682, for each stimulus, we draw three observations --human binary answer-- without replacement).
  In the paper, we provide only the mean log-likelihood obtained by this resampling, but here we present the mean differences between
   models, and indicate if the difference is significant. The following table contains the mean of the differences. The values are in bold if the difference is significant (ie if the 95% interval is above zero).

 |   |  MFCC   | P2 | P1  | Y2   | Y1   | C2   | Y3    | C1   | A3   | H   | S1   | Bot   | DP   | S2 | 
  --- |  --- | --- | ---  | ---  | ---   | ---  |  ---  | ---   | ---  | --- | --- | --- | --- | ---|
 topline | **63.3** | **91.1** | **85.9** | **106.8** | **100.0** | **107.1** | **110.8** | **124.3** | **160.5** | **177.4** | **212.0** | **216.3** | **236.3** | **252.1** | 
 MFCC | - | **27.8** | **22.5** | **43.5** | **36.7** | **43.8** | **47.5** | **61.0** | **97.2** | **114.1** | **148.7** | **153.0** | **173.0** | **188.8** | 
 P2 |  | - | -5.2 | 15.7 | 8.9 | 16.0 | 19.7 | **33.1** | **69.4** | **86.3** | **120.9** | **125.2** | **145.1** | **160.9** | 
 P1 |  |  | - | 20.9 | 14.1 | 21.2 | **24.9** | **38.3** | **74.6** | **91.5** | **126.1** | **130.4** | **150.4** | **166.2** | 
 Y2 |  |  |  | - | -6.7 | 0.3 | 4.0 | **17.5** | **53.7** | **70.6** | **105.2** | **109.6** | **129.5** | **145.2** | 
 Y1 |  |  |  |  | - | 7.1 | 10.8 | **24.2** | **60.4** | **77.4** | **112.0** | **116.3** | **136.2** | **152.0** | 
 C2 |  |  |  |  |  | - | 3.7 | **17.1** | **53.4** | **70.3** | **104.9** | **109.2** | **129.1** | **144.9** | 
 Y3 |  |  |  |  |  |  | - | **13.4** | **49.7** | **66.5** | **101.2** | **105.5** | **125.4** | **141.2** | 
 C1 |  |  |  |  |  |  |  | - | **36.2** | **53.2** | **87.7** | **92.1** | **112.0** | **127.8** | 
 A3 |  |  |  |  |  |  |  |  | - | 16.8 | **51.5** | **55.8** | **75.7** | **91.5** | 
 H |  |  |  |  |  |  |  |  |  | - | **34.6** | **38.9** | **58.8** | **74.6** | 
 S1 |  |  |  |  |  |  |  |  |  |  | - | 4.4 | 24.3 | **40.1** | 
 Bot |  |  |  |  |  |  |  |  |  |  |  | - | 19.9 | **35.7** | 
 DP |  |  |  |  |  |  |  |  |  |  |  |  | - | 15.8 | 
 
