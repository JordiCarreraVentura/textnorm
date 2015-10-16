

##	Summary
This repository contains Textnorm (after "[text] [norm]alization"), a Python class for detecting multiword expressions over a large corpus of raw free text.

##	Description and Examples
A multiword expression is a sequence of words that show a significantly high statistical association and tend to appear together much more often than chance. Multiwords are a superset of compounds ("chicken soup"), idioms ("kick the bucket"), phrasal verbs ("come up with"), collocations ("extraordinary circumstances" versus "uncommon circumstances" -both combinations are largely semantically equivalent yet the first one is usually preferred-), standard multiword entities ("Barack Obama", "Barack H. Obama", "Obama", "Mr. Barack Hussein Obama" and "President Obama" all behave like single units *despite* the white space).

In many cases, word tokenization (naïvely performed by splitting at white spaces) results in linguistically incorrect statistics. As an example, when calculating the most frequent words in a text, naïve word tokenization will yield "Barack" as a word with a certain frequency, and "Obama" as another word with a frequency very close to that of the former (but not necessarily the same because their distribution pattern is not bi-univocal). What we want is rather a single token with a single frequency count. Ultimately, this can have significant consequences for any statistical approaches which rely on the independence assumption, such as Naïve Bayes and Logistic Regression.
-------VERIFY INDEPENDENCE ASSUMPTION FOR LOGISTIC REGRESSION

Put another way, the goal of this library is to minimize the discrepancy between claim i) "white spaces separate words" and ii) "white spaces separate distinct linguistic units". In the standard written form of most languages, cases of claim ii) are only a subset of the cases of claim i) and the difference stands for errors in linguistic analysis.

Textnorm both detects the likely multiword candidates and maps the annotation onto the original file, returning a copy of the input text with all multiwords marked as sequences of words now connected with underscores, as shown in the following example:

<quote>
### Input
> You want to drive_a_car--gotta have car_insurance.  You want to live--gotta pay the bare bones insurance premium to live.  When you don't pay and you get sick and have to go to the_emergency_room, you're a burden on the system.  Gotta change that.  The_emergency_room is for people like my old neighbors--they loved setting off firecrackers and every once in a while they had to wrap someone's bloody hand in a t-shirt and take them to the_emergency_room.

### Output
> You want to drive_a_car--gotta have car_insurance.  You want to live--gotta pay the bare bones insurance premium to live.  When you don't pay and you get sick and have to go to the_emergency_room, you're a burden on the system.  Gotta change that.  The_emergency_room is for people like my old neighbors--they loved setting off firecrackers and every once in a while they had to wrap someone's bloody hand in a t-shirt and take them to the_emergency_room.

More examples are provided at the bottom.


##	Usage

### Running the script with default parameters

	python textnorm.py -i PATH/TO/INPUT/FILE

The output is stored by default in a PATH/TO/INPUT/FILE".textnorm.txt". Alternatively, a different location for the output can be specified by using the flag "-o" during invocation as shown below:

	python textnorm.py -i PATH/TO/INPUT/FILE -o PATH/TO/OUTPUTFILE

When invoking Textnorm in this way, the system will auto-configure its parameters following a small set of statistical assumptions that usually hold for most natural language text across a variety of settings. During testing, the default parameters have provided (subjectively) good results with inputs as diverse as e-commerce titles and blog posts, although substantial fluctuations can be expected for varying sample sizes and different degrees of text naturalness.


## Description of parameters and advanced settings


#	Script arguments

flag | description | required/optional | comments | default
-i | Input file | string | required | Path of a file containing raw text to be used as input. | No default.
-o | Output file | string | optional |Path of the file where the system's output should be stored. | Defaults to the input file
-t | string | optional |Path of the file where the system's output should be stored. | Defaults to the input file
            '-i': 'corpus',
            '-o': 'out',
            '-t': 'tmp',
            '--maxk': 'maxk',
            '--flush': 'flush',
            '--silent': 'silent',
            '-n': 'ngrams',
            '--ndocs': 'ndocs',
            '--maxf': 'maxf',
            '--minf': 'minf',
            '--smooth': 'smooth'
        }
        self.parsers = {
            '-i': None,
            '-o': None,
            '-t': None,
            '--maxk': self.integer,
            '--flush': self.flush,
            '-n': self.integer,
            '--ndocs': self.integer,
            '--maxf': self.floatint,
            '--minf': self.integer,
            '--smooth': self.autofloat




        # -i            corpus
        # -o            out, default out wrt corpus
        # -t            tmp, default tmp wrt corpus
        # --maxk        (max_k, max_f, min_f) or 'auto'
        # --flush       flushing ratio, default (1, 200000)
        # --silent      silent, default verbose
        # -n            ngrams, default 10
        # --ndocs       ndocs, default None




CORPUS = File containing the input corpus
OUT = File where the output will be stored
TMP = Temporary file for storing the postprocessed data.

 'work.temp.dat'

#	Model parameters
N = Maximum order of n-grams to be computed for multiword extraction. By the definition of multiwords, the minimum order is hard-coded to 2.

F = Minimum frequency for a multiword
Top F word n-grams most activated by their character n-grams that will be pooled for rewriting.

MAX_K = 100

MAX_F = float or int
Maximum frequency for any unigram. Unigrams with a frequency equal or higher than this number will not be considered content words and will be omitted as multiword anchors. They can still appear inside multiwords, but they will not appear at either their beginning or end.
If a float is provided (0 ≥ MAX_F ≥ 1.0), the final parameter will be calculated as the number of document lines in the input corpus times the initial floating point parameter.

N_DOCS = 5000
Maximum number of document lines to be streamed from the input file. This is useful in cases in which the input corpus is extremely large (in the current version, processing 5 million sentences requires 8GB of RAM).

UPDATE: with flushing of infrequent n-grams, the memory footprint has decreased to: 



=================
HOWTO DOCSTRING

"def add(x, y):
    """Return the sum of x and y."""
    return x + y


================= Textnorm class

================= Move ArgumentParser out

================= Samples



The only person exempted from that restriction is the American ambassador to Iraq, Ryan_Crocker, who can discuss Iraq-related issues with Iranian officials on a_regular_basis, according to a State_Department_official in Washington who spoke_on_condition_of_anonymity.Ambassador Khalilzad aroused the ire of Secretary_Rice who is reportedly upset that such a high ranking American official would participate in the same forum as the Iranian_foreign_minister. Mr. Khalilzad did not stray from American talking points at the forum. But Powerline is reporting that the moderator of the panel_discussion, the head_of_the_International Crisis Group Gareth Evans, insulted former UN_Ambassador John Bolton.

"Revolutionary_Armed_Forces_of_Colombia" and their mission of violence:"Founded in 1964, the FARC is a self-proclaimed communist and revolutionary guerrilla organization. They claim_to_represent the poor in their struggle against the country's wealthier classes, striving to seize power through armed revolution. These declarations notwithstanding, however, the group has largely abandoned its political agenda, and the FARC are now merely a drug_trafficking and terrorist group with complete_disregard for human_rights_and_international humanitarian law. Since the late 1980s, the Colombian government has repeatedly attempted to negotiate a solution and peace_settlement, without success. Directly_or_indirectly, all Colombians, including those of us here in Princeton, have been affected by their inhumane actions."My article from 2006 on the general topic can be accessed via this link.Ari J. Kaufman

On Super_Tuesday, 22 states and a couple territories with a combined 1,688 pledged_delegates will hold nominating_contests. From this point, quick math shows that after Super_Tuesday, only 1,428 pledged_delegates will still be available. Now, here is where the problem shows up. According to current_polling averages, the largest_possible victory for either candidate on Super_Tuesday will be Clinton 889 pledged_delegates, to 799 pledged_delegates for Obama. (In all likelihood, the winning margin will be lower than this, but using these numbers helps emphasize the seriousness_of_the_situation.)
Power advised Obama on foreign policy, having spent her career detailing genocides and international responses to them, including a Pulitzer_Prize-winning book_on_the_subject.

A new video has Barack Obama speaking in 2007 about the burgeoning crisis in the financial_markets, but focusing on accounting_fraud rather than the_root_cause of the meltdown: the widespread issuance of bad credit, securitized by Fannie_Mae_and_Freddie_Mac at the behest of Congress.  In this audio_clip, Obama defends the idea of subprime_lending just over a year ago:

Iran has watched the drop_in_oil_prices with growing_alarm, the_International_Herald-Tribune reports, and it wants OPEC to take action to support prices at higher than $100 per_barrel. 

The anger generated from that information has nothing to do with racism, and everything to do with the breach_of_trust between Congress and its constituents.  Frank, Chris_Dodd, and others like Lacy_Clay and Maxine_Waters tried the racist meme out on regulators who tried_to_warn Congress of the pending collapse.  They have to smear their critics.  They certainly can’t admit that Congress failed spectacularly.

With Congress grilling Wall_Street_executives over the_financial_collapse, why not have some of the real culprits testify in their investigations?  One of them is close at hand; in fact, he’s pretending to lead the investigation while really being one of its best targets.  Senator Chris_Dodd took massive_amounts in political contributions from Fannie_Mae, Freddie_Mac, and Countrywide, while securing sweetheart_deals from that same lender, all while supposedly providing the oversight that somehow missed the rotten struts under the entire subprime_market.  The_Wall_Street_Journal wonders why Dodd’s asking_questions rather than answering them:Dodd should get expelled first for his conflict_of_interest in accepting his sweetheart loans_from_Countrywide in the “Friends of Angelo” program. 