"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  Activity,
  Brain,
  FlaskConical,
  Target,
} from "lucide-react";

import Navbar from "@/components/Navbar";

import {
  AuthState,
  apiFetch,
  getAuthState,
} from "@/lib/api";


type Lang = "en" | "ar";


type Insights = {
  totalScans: number;
  averageShift: number;
  largestShift: number;

  aggregated: {
    id: string;
    name: string;
    probability: number;
    observations: number;
  }[];

  scenarioCoverage: {
    id: string;
    title: string;
    count: number;
  }[];
};



export default function DashboardPage() {


  const [data, setData] = useState<Insights | null>(null);

  const [auth, setAuth] = useState<AuthState>({
    authenticated: false,
  });

  const [lang, setLang] = useState<Lang>("en");



  useEffect(() => {

    const savedLang =
      window.localStorage.getItem("mri_lang");


    if (
      savedLang === "ar" ||
      savedLang === "en"
    ) {
      setLang(savedLang);
    }


    async function load() {

      const [
        authState,
        res,
      ] = await Promise.all([
        getAuthState(),
        apiFetch("/api/insights", {
          cache: "no-store",
        }),
      ]);


      setAuth(authState);


      if (res.ok) {
        setData(await res.json());
      }

    }


    load();


  }, []);



  function toggleLanguage() {

    const next =
      lang === "en"
        ? "ar"
        : "en";


    setLang(next);


    window.localStorage.setItem(
      "mri_lang",
      next
    );

  }




  function openPlatformView(
    view:
      | "home"
      | "lab"
      | "insights"
      | "system"
  ) {

    window.location.href =
      view === "home"
        ? "/"
        : `/?view=${view}`;

  }



  function openStem() {

    window.location.href = "/stem";

  }




  const labels = {

    navHome:
      lang === "ar"
        ? "الرئيسية"
        : "Home",


    navLab:
      lang === "ar"
        ? "مختبر التشخيص"
        : "Diagnostic Lab",


    navInsights:
      lang === "ar"
        ? "التحليلات"
        : "Insights",


    navSystem:
      lang === "ar"
        ? "النظام"
        : "System",

  };




  return (

    <main
      className="site"
      dir={
        lang === "ar"
          ? "rtl"
          : "ltr"
      }
    >


      <Navbar

        activeView="insights"

        labels={labels}

        auth={auth}

        lang={lang}


        onHome={() =>
          openPlatformView("home")
        }


        onLab={() =>
          openPlatformView("lab")
        }


        onStem={openStem}


        onInsights={() =>
          openPlatformView("insights")
        }


        onSystem={() =>
          openPlatformView("system")
        }


        onToggleLanguage={
          toggleLanguage
        }

      />



      <section className="dashboard-page">


        {!data ? (

          "Loading intelligence profile..."


        ) : (


          <>


            <header className="dashboard-header">

              <div>

                <span className="eyebrow">
                  LEARNER INTELLIGENCE
                </span>


                <h1>
                  Your Cognitive Profile
                </h1>


                <p>
                  Track your misconceptions and learning progress.
                </p>

              </div>



              <Link
                href="/?view=lab"
                className="primary"
              >
                New Scan
              </Link>


            </header>





            <section className="stats-grid">


              <div className="stat-card">

                <Brain />

                <span>
                  Total Scans
                </span>

                <strong>
                  {data.totalScans}
                </strong>

              </div>




              <div className="stat-card">


                <Activity />


                <span>
                  Average Learning Shift
                </span>


                <strong>
                  {
                    (
                      data.averageShift * 100
                    ).toFixed(1)
                  }%
                </strong>


              </div>





              <div className="stat-card">


                <Target />


                <span>
                  Largest Improvement
                </span>


                <strong>
                  {
                    (
                      data.largestShift * 100
                    ).toFixed(1)
                  }%
                </strong>


              </div>


            </section>





            <section className="dashboard-grid">


              <div className="panel">


                <h2>
                  Misconception Map
                </h2>



                {
                  data.aggregated.length === 0 &&
                  <p>
                    No scans yet.
                  </p>
                }



                {
                  data.aggregated.map(
                    item => (

                      <div
                        className="progress-item"
                        key={item.id}
                      >


                        <div>

                          <span>
                            {item.name}
                          </span>


                          <b>
                            {
                              (
                                item.probability * 100
                              ).toFixed(0)
                            }%
                          </b>


                        </div>



                        <div className="bar">

                          <div

                            className="fill"

                            style={{
                              width:
                                `${
                                  item.probability * 100
                                }%`
                            }}

                          />

                        </div>



                        <small>
                          {item.observations}
                          {" "}
                          observations
                        </small>


                      </div>

                    )
                  )
                }


              </div>






              <div className="panel">


                <h2>
                  STEM Learning Coverage
                </h2>



                {
                  data.scenarioCoverage.map(
                    item => (

                      <div

                        className="coverage-item"

                        key={item.id}

                      >

                        <FlaskConical />


                        <div>

                          <strong>
                            {item.title}
                          </strong>


                          <span>
                            {item.count}
                            {" "}
                            attempts
                          </span>


                        </div>


                      </div>

                    )
                  )
                }


              </div>


            </section>


          </>

        )}


      </section>


    </main>

  );


}