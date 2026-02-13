
from pydantic import BaseModel
from typing import List, Optional

class HeroComponent(BaseModel):
    headline: str
    subheadline: str
    cta_text: str
    image_url: str

class Feature(BaseModel):
    title: str
    description: str
    icon: str

class FeatureComponent(BaseModel):
    title: str
    features: List[Feature]

class PricingOption(BaseModel):
    name: str
    price: str
    description: str
    features: List[str]
    is_popular: bool = False

class PricingComponent(BaseModel):
    options: List[PricingOption]

class LandingPageComponentSet(BaseModel):
    hero: HeroComponent
    features: FeatureComponent
    pricing: PricingComponent
    footer_text: str

class ComponentTemplates:
    
    @staticmethod
    def render_hero(data: HeroComponent) -> str:
        return f"""
        <section class="relative bg-black overflow-hidden py-24 sm:py-32">
            <div class="mx-auto max-w-7xl px-6 lg:px-8">
                <div class="mx-auto max-w-2xl text-center">
                    <h1 class="text-4xl font-bold tracking-tight text-white sm:text-6xl bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                        {data.headline}
                    </h1>
                    <p class="mt-6 text-lg leading-8 text-gray-300">
                        {data.subheadline}
                    </p>
                    <div class="mt-10 flex items-center justify-center gap-x-6">
                        <a href="#" class="rounded-md bg-emerald-500 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-emerald-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400 transition-all duration-300 transform hover:scale-105">
                            {data.cta_text}
                        </a>
                    </div>
                </div>
            </div>
            <div class="absolute inset-x-0 top-0 -z-10 transform-gpu overflow-hidden blur-3xl" aria-hidden="true">
                <div class="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#00ff88] to-[#00ffff] opacity-20 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"></div>
            </div>
        </section>
        """

    @staticmethod
    def render_features(data: FeatureComponent) -> str:
        feature_html = ""
        for f in data.features:
            feature_html += f"""
            <div class="relative pl-16">
                <dt class="text-base font-semibold leading-7 text-white">
                    <div class="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500">
                        <i class="fas {f.icon} text-white"></i>
                    </div>
                    {f.title}
                </dt>
                <dd class="mt-2 text-base leading-7 text-gray-400">{f.description}</dd>
            </div>
            """
        
        return f"""
        <section class="py-24 sm:py-32 bg-gray-900">
            <div class="mx-auto max-w-7xl px-6 lg:px-8">
                <div class="mx-auto max-w-2xl lg:text-center">
                    <h2 class="text-base font-semibold leading-7 text-emerald-400">Deploy Faster</h2>
                    <p class="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">{data.title}</p>
                </div>
                <div class="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
                    <dl class="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-2 lg:gap-y-16">
                        {feature_html}
                    </dl>
                </div>
            </div>
        </section>
        """

    @staticmethod
    def render_pricing(data: PricingComponent) -> str:
        pricing_html = ""
        for opt in data.options:
            border = "border-emerald-500 ring-2 ring-emerald-500" if opt.is_popular else "border-gray-800"
            pricing_html += f"""
            <div class="flex flex-col justify-between rounded-3xl bg-gray-900 p-8 ring-1 ring-gray-200/10 xl:p-10 {border} transition-all duration-300 hover:transform hover:-translate-y-2">
                <div>
                    <div class="flex items-center justify-between gap-x-4">
                        <h3 id="tier-startup" class="text-lg font-semibold leading-8 text-white">{opt.name}</h3>
                        {"<p class='rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold leading-5 text-emerald-400'>Most Popular</p>" if opt.is_popular else ""}
                    </div>
                    <p class="mt-4 text-sm leading-6 text-gray-400">{opt.description}</p>
                    <p class="mt-6 flex items-baseline gap-x-1">
                        <span class="text-4xl font-bold tracking-tight text-white">{opt.price}</span>
                    </p>
                    <ul role="list" class="mt-8 space-y-3 text-sm leading-6 text-gray-400">
                        {" ".join([f'<li class="flex gap-x-3"><i class="fas fa-check text-emerald-500"></i>{feat}</li>' for feat in opt.features])}
                    </ul>
                </div>
                <a href="#" class="mt-8 block rounded-md py-2 px-3 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 {"bg-emerald-500 text-white shadow-sm hover:bg-emerald-400" if opt.is_popular else "bg-white/10 text-white hover:bg-white/20"}">
                    Get started
                </a>
            </div>
            """

        return f"""
        <div class="bg-gray-950 py-24 sm:py-32">
            <div class="mx-auto max-w-7xl px-6 lg:px-8">
                <div class="mx-auto max-w-4xl text-center">
                    <h2 class="text-base font-semibold leading-7 text-emerald-400">Pricing</h2>
                    <p class="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">Plans that scale with you</p>
                </div>
                <div class="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3 lg:gap-x-8">
                    {pricing_html}
                </div>
            </div>
        </div>
        """

    @staticmethod
    def render_full_page(components: str, title: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="en" class="h-full bg-black">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Inter', sans-serif; }}
                ::-webkit-scrollbar {{ width: 10px; }}
                ::-webkit-scrollbar-track {{ background: #000; }}
                ::-webkit-scrollbar-thumb {{ background: #10b981; border-radius: 5px; }}
            </style>
        </head>
        <body class="selection:bg-emerald-500/30">
            {components}
            <footer class="bg-black py-12 border-t border-gray-800">
                <div class="mx-auto max-w-7xl px-6 lg:px-8 text-center text-gray-500 text-sm">
                    &copy; 2026 {title}. Built by IdeaLab Strategic Agent.
                </div>
            </footer>
        </body>
        </html>
        """
