"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import { getAuthState, AuthState, apiFetch } from "@/lib/api";
import {
  Atom,
  Calculator,
  Cpu,
  Leaf,
  Cog,
} from "lucide-react";


type Domain = {
  id: string;
  name: string;
  description: string;
  icon: string;
};


type Lang = "en" | "ar";


export default function STEMPage() {

  const [domains, setDomains] = useState<Domain[]>([]);
  const [auth, setAuth] = useState<AuthState>({
    authenticated: false,
  });

  const [lang, setLang] = useState<Lang>("en");


  useEffect(() => {

    async function load() {

      const [
        authState,
        response
      ] = await Promise.all([
        getAuthState(),
        apiFetch("/api/domains")
      ]);


      setAuth(authState);


      if (response.ok) {
        setDomains(await response.json());
      }

    }


    load();

  }, []);



  function toggleLanguage(){

    const next =
      lang === "en"
        ? "ar"
        : "en";

    setLang(next);

    localStorage.setItem(
      "mri_lang",
      next
    );

  }



  function iconFor(name:string){

    if(name==="Physics")
      return <Atom size={32}/>;

    if(name==="Mathematics")
      return <Calculator size={32}/>;

    if(name==="Engineering")
      return <Cog size={32}/>;

    if(name==="Technology")
      return <Cpu size={32}/>;

    return <Leaf size={32}/>;

  }



  const labels = {

    navHome:
      lang==="ar"
      ? "الرئيسية"
      : "Home",

    navLab:
      lang==="ar"
      ? "مختبر التشخيص"
      : "Diagnostic Lab",

    navInsights:
      lang==="ar"
      ? "التحليلات"
      : "Insights",

    navSystem:
      lang==="ar"
      ? "النظام"
      : "System",

  };



  return (

    <main className="site">


      <Navbar

        activeView="stem"

        labels={labels}

        auth={auth}

        lang={lang}

        onHome={() =>
          window.location.href="/"
        }

        onLab={() =>
          window.location.href="/?view=lab"
        }

        onStem={() =>
          window.location.href="/stem"
        }

        onInsights={() =>
          window.location.href="/?view=insights"
        }

        onSystem={() =>
          window.location.href="/?view=system"
        }

        onToggleLanguage={
          toggleLanguage
        }

      />



      <section className="stem-page">


        <header className="stem-header">

          <span className="eyebrow">
            STEM INTELLIGENCE
          </span>


          <h1>
            Explore STEM Domains
          </h1>


          <p>
            Expand cognitive diagnostics beyond physics into a complete STEM learning intelligence platform.
          </p>


        </header>




        <div className="stem-grid">


          {
            domains.map(domain => (

              <Link

                href={`/stem/${domain.name.toLowerCase()}`}

                key={domain.id}

                className="stem-card"

              >

                <div className="stem-icon">

                  {iconFor(domain.name)}

                </div>


                <h2>
                  {domain.name}
                </h2>


                <p>
                  {domain.description}
                </p>


              </Link>

            ))
          }


        </div>


      </section>


    </main>

  );

}