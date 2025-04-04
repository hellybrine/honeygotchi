export default function Hero() {
    return (
      <section className="mt-20 text-center px-10">
        <h1 className="text-4xl font-bold">
          Software engineer, technical writer & open-source maintainer
        </h1>
        <p className="mt-4 text-gray-400">
          I'm Victor Eke, an experienced frontend developer passionate about learning and building open-source software.
        </p>
  
        <div className="flex justify-center space-x-4 mt-6">
          {["GitHub", "LinkedIn", "CodePen", "Dribbble"].map((item) => (
            <a key={item} href="#" className="bg-gray-800 p-2 rounded hover:bg-gray-700">
              {item}
            </a>
          ))}
        </div>
      </section>
    );
  }  