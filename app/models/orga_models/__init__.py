from .dao import Dao
from .entreprise import Entreprise
from .ngo import Ngo
from .public_company import PublicCompany

governances = {
	"ngo": {
		"templateClass": Ngo,
		"rulesContract": "OpenRegistryRules",
		"registryContract": "OpenRegistry",
		"tokenContract": None
		},
	"dao": {
		"templateClass": Dao,
		"rulesContract": "LiquidDemocracyRules", #DAO.sol à terme
		"registryContract": None,
		"tokenContract": None
		},
	# "entreprise": {
		# "templateClass": Entreprise,
	# 	"rulesContract": "ControlledRegistryRules",
	# 	"registryContract": "ControlledRegistry",
	# 	"tokenContract": None
	# 	},
	"public_company": {
		"templateClass": PublicCompany,
		"rulesContract": "LiquidDemocracyRules",
		"registryContract": None,
		"tokenContract": None
		}
}