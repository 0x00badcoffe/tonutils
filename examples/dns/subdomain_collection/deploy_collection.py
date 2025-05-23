from tonutils.client import TonapiClient
from tonutils.dns import Domain
from tonutils.dns.subdomain_collection import SubdomainCollection
from tonutils.dns.subdomain_collection.content import SubdomainCollectionContent
from tonutils.dns.subdomain_collection.data import FullDomain
from tonutils.nft.royalty_params import RoyaltyParams
from tonutils.wallet import WalletV4R2
from tonutils.wallet.data import TransferData

# API key for accessing the Tonapi (obtainable from https://tonconsole.com)
API_KEY = ""

# Set to True for test network, False for main network
IS_TESTNET = True

# Mnemonic phrase used to connect the wallet
MNEMONIC: list[str] = []

# NFT domain name and address from TON DNS Domains
# Obtainable from https://dns.ton.org/ or https://dns.ton.org/?testnet=true
DOMAIN_NAME = "ghost"  # ghost → ghost.ton
DOMAIN_ADDRESS = "EQ..."

# Royalty parameters: base and factor for calculating the royalty
ROYALTY_BASE = 1000
ROYALTY_FACTOR = 55  # 5.5% royalty

# The base URL of the API for generating metadata for NFTs.
# API source code: https://github.com/nessshon/subdomains-toolbox
API_BASE_URL = "https://dns.ness.su/api/ton/"

# Metadata for the NFT collection
COLLECTION_METADATA = {
    "name": f"{DOMAIN_NAME.title()} DNS Domains",
    "image": f"{API_BASE_URL}{DOMAIN_NAME}.png",
    "description": f"*.{DOMAIN_NAME}.ton domains",
    "prefix_uri": API_BASE_URL,
}
"""
{
    "name": "Ghost DNS Domains",
    "image": "https://dns.ness.su/api/ton/ghost.png",
    "description": "*.ghost.ton domains",
    "prefix_uri": "https://dns.ness.su/api/ton/"
}
"""


async def main() -> None:
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)
    wallet, _, _, _ = WalletV4R2.from_mnemonic(client, MNEMONIC)

    collection = SubdomainCollection(
        owner_address=wallet.address,
        content=SubdomainCollectionContent(**COLLECTION_METADATA),
        royalty_params=RoyaltyParams(
            base=ROYALTY_BASE,
            factor=ROYALTY_FACTOR,
            address=wallet.address,
        ),
        full_domain=FullDomain(DOMAIN_NAME, "ton"),
    )

    tx_hash = await wallet.batch_transfer(
        [
            # Deploy collection
            TransferData(
                destination=collection.address,
                amount=0.05,
                body=collection.build_deploy_body(),
                state_init=collection.state_init,
            ),
            # Binding a Subdomain Collection to the main domain
            TransferData(
                destination=DOMAIN_ADDRESS,
                amount=0.05,
                body=Domain.build_set_next_resolver_record_body(collection.address),
            ),
        ]
    )

    print(f"Successfully deployed Subdomain Collection at address: {collection.address.to_str()}")
    print(f"Transaction hash: {tx_hash}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
