from .dao import Dao
from .entreprise import Entreprise
from .ngo import Ngo
from .public_company import PublicCompany

governances = {
	"ngo": {
		"templateClass": Ngo,
		"rulesContract": "OpenRegistryRules",
		"registryContract": "OpenRegistry",
		"tokenContract": None,
		"tokenFreezerContract": None
		},
	"dao": {
		"templateClass": Dao,
		"rulesContract": "TokenFreezerRules",
		"registryContract": None,
		"tokenContract": "StandardToken",
		"tokenFreezerContract": "StandardTokenFreezer"
		},
	"entreprise": {
		"templateClass": Entreprise,
		"rulesContract": "ControlledRegistryRules",
		"registryContract": "ControlledRegistry",
		"tokenContract": None,
		"tokenFreezerContract": None
		},
	"public_company": {
		"templateClass": PublicCompany,
		"rulesContract": "LiquidDemocracyRules",
		"registryContract": None,
		"tokenContract": "StandardToken",
		"tokenFreezerContract": "StandardTokenFreezer"
		}
}