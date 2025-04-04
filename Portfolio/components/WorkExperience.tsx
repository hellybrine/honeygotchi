export default function WorkExperience() {
    const jobs = [
      { title: "Optimus AI Lab", role: "Mid-level Frontend Engineer", period: "Nov 2024 - Jan 2025" },
      { title: "Paydesta", role: "Frontend Developer", period: "Sep 2024 - Present" },
      { title: "Educative", role: "Project Author", period: "Dec 2023 - Sep 2024" },
      { title: "freeCodeCamp", role: "Technical Writer", period: "Aug 2022 - Dec 2023" },
    ];
  
    return (
      <section className="mt-20 px-10">
        <h2 className="text-2xl font-bold">Work Experience</h2>
        <div className="mt-6 space-y-4">
          {jobs.map(({ title, role, period }) => (
            <div key={title} className="bg-gray-900 p-4 rounded">
              <h3 className="font-bold">{title}</h3>
              <p className="text-gray-400">{role} ({period})</p>
            </div>
          ))}
        </div>
      </section>
    );
  }  