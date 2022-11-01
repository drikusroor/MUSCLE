from .beat_alignment import BeatAlignment
from .speech2song import Speech2Song
from .duration_discrimination import DurationDiscrimination
from .duration_discrimination_tone import DurationDiscriminationTone
from .anisochrony import Anisochrony
from .categorization import Categorization
from .gold_msi import GoldMSI
from .h_bat import HBat
from .h_bat_bfit import HBatBFIT
from .hbat_bst import BST
from .huang_2022 import Huang2022
from .listening_conditions import ListeningConditions
from .matching_pairs import MatchingPairs
from .musical_preferences import MusicalPreferences
from .rhythm_discrimination import RhythmDiscrimination
from .rhythm_experiment_series import RhythmExperimentSeries
from .rhythm_experiment_series_mri import RhythmExperimentSeriesMRI
from .rhythm_experiment_series_unpaid import RhythmExperimentSeriesUnpaid
from .toontjehoger_1_mozart import ToontjeHoger1Mozart
from .toontjehoger_3_plink import ToontjeHoger3Plink
from .toontjehoger_6_relative import ToontjeHoger6Relative


# Rules available to this application
# If you create new Rules, add them to the list
# so they can be referred to by the admin

EXPERIMENT_RULES = {
    BeatAlignment.ID: BeatAlignment,
    Speech2Song.ID: Speech2Song,
    DurationDiscrimination.ID: DurationDiscrimination,
    DurationDiscriminationTone.ID: DurationDiscriminationTone,
    Anisochrony.ID: Anisochrony,
    HBat.ID: HBat,
    HBatBFIT.ID: HBatBFIT,
    BST.ID: BST,
    MatchingPairs.ID: MatchingPairs,
    MusicalPreferences.ID: MusicalPreferences,
    RhythmDiscrimination.ID: RhythmDiscrimination,
    RhythmExperimentSeries.ID: RhythmExperimentSeries,
    RhythmExperimentSeriesMRI.ID: RhythmExperimentSeriesMRI,
    RhythmExperimentSeriesUnpaid.ID: RhythmExperimentSeriesUnpaid,
    GoldMSI.ID: GoldMSI,
    ListeningConditions.ID: ListeningConditions,
    Huang2022.ID: Huang2022,
    Categorization.ID: Categorization,
    ToontjeHoger1Mozart.ID: ToontjeHoger1Mozart,
    ToontjeHoger3Plink.ID: ToontjeHoger3Plink,
    ToontjeHoger6Relative.ID: ToontjeHoger6Relative,
}
