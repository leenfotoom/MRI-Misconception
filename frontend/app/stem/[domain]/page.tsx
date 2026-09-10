"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import { useEffect, useState } from "react";
import { AuthState, getAuthState } from "@/lib/api";

import {
  Atom,
  Calculator,
  Cog,
  Cpu,
  Leaf,
  Play,
} from "lucide-react";


type Lang = "en" | "ar";


const domains: Record<
  string,
  {
    title: string;
    description: string;
    icon: React.ReactNode;
    modules: string[];
  }
> = {

  physics: {
    title: "Physics Intelligence",
    description:
      "Understand physical systems, energy, motion and scientific reasoning.",
    icon: <Atom size={40}/>,
    modules:[
      "Motion & Forces",
      "Energy Systems",
      "Waves",
      "Electricity"
    ]
  },


  mathematics:{
    title:"Mathematics Intelligence",
    description:
      "Develop mathematical reasoning, logic and problem solving.",
    icon:<Calculator size={40}/>,
    modules:[
      "Algebra",
      "Functions",
      "Logic",
      "Problem Solving"
    ]
  },


  engineering:{
    title:"Engineering Intelligence",
    description:
      "Explore design thinking and applied engineering concepts.",
    icon:<Cog size={40}/>,
    modules:[
      "Systems",
      "Structures",
      "Design",
      "Optimization"
    ]
  },


  technology:{
    title:"Technology Intelligence",
    description:
      "Programming, AI and digital systems reasoning.",
    icon:<Cpu size={40}/>,
    modules:[
      "Programming",
      "Artificial Intelligence",
      "Databases",
      "Networks"
    ]
  },


};



export default function DomainPage(){


  const params = useParams();

  const domain =
    params.domain as string;


  const data =
    domains[domain] || domains.physics;



  const [auth,setAuth] =
    useState<AuthState>({
      authenticated:false
    });


  const [lang,setLang] =
    useState<Lang>("en");



  useEffect(()=>{

    getAuthState()
      .then(setAuth);

  },[]);



  function toggleLanguage(){

    const next =
      lang==="en"
      ?"ar"
      :"en";

    setLang(next);

    localStorage.setItem(
      "mri_lang",
      next
    );
  }



  const labels = {

    navHome:"Home",
    navLab:"Diagnostic Lab",
    navInsights:"Insights",
    navSystem:"System"

  };



  return (

    <main className="site">


      <Navbar

        activeView="stem"

        labels={labels}

        auth={auth}

        lang={lang}

        onHome={()=>
          window.location.href="/"
        }

        onLab={()=>
          window.location.href="/?view=lab"
        }

        onStem={()=>
          window.location.href="/stem"
        }

        onInsights={()=>
          window.location.href="/?view=insights"
        }

        onSystem={()=>
          window.location.href="/?view=system"
        }

        onToggleLanguage={
          toggleLanguage
        }

      />



      <section className="domain-page">


        <div className="domain-hero">


          <div className="domain-icon">

            {data.icon}

          </div>


          <h1>
            {data.title}
          </h1>


          <p>
            {data.description}
          </p>



          <Link
            href={`/?view=lab&domain=${domain === "physics" ? "science" : domain}`}
            className="primary"
          >

            <Play size={16}/>

            Start Diagnostic Scan

          </Link>


        </div>




        <div className="module-grid">


          {
            data.modules.map(
              module=>(
                <div
                  key={module}
                  className="module-card"
                >

                  {module}

                </div>
              )
            )
          }


        </div>


      </section>


    </main>

  );

}
