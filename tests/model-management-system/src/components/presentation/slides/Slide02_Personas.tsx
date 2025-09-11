import React from 'react';
import SlideTemplate from '../SlideTemplate';
import { RequestorIcon, ManagerIcon, DataProviderIcon, EngineerIcon, personaColors } from '../../ui/Icons';

const PersonasSlide: React.FC = () => {
  const personas = [
    {
      title: 'Requestor',
      IconComponent: RequestorIcon,
      colorKey: 'requestor',
      roles: ['Technical Marketing', 'Project Manager', 'Application Engineer'],
      activities: [
        'Initiates model requests for new products',
        'Defines requirements and specifications',
        'Tracks progress and validates deliverables'
      ]
    },
    {
      title: 'Manager',
      IconComponent: ManagerIcon,
      colorKey: 'manager',
      roles: ['Team Lead', 'Department Head', 'Project Director'],
      activities: [
        'Monitors work progress and KPIs',
        'Allocates resources and priorities',
        'Reviews reports and metrics'
      ]
    },
    {
      title: 'Data Provider',
      IconComponent: DataProviderIcon,
      colorKey: 'dataProvider',
      roles: ['Lab Engineer', 'TCAD Engineer', 'Concept Engineer'],
      activities: [
        'Provides measurement data from lab',
        'Supplies TCAD simulation results',
        'Validates data quality and formats'
      ]
    },
    {
      title: 'Modeling Engineer',
      IconComponent: EngineerIcon,
      colorKey: 'engineer',
      roles: ['Device Modeling Expert', 'Calibration Specialist', 'Parameter Extraction'],
      activities: [
        'Performs model calibration and optimization',
        'Validates model accuracy and quality',
        'Ensures models meet specifications'
      ]
    }
  ];

  return (
    <SlideTemplate 
      title="Platform Users & Roles"
      backgroundColor="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50"
    >
      <div>
        <div className="grid grid-cols-4 gap-10">
          {personas.map((persona, index) => {
            const colors = personaColors[persona.colorKey as keyof typeof personaColors];
            const IconComponent = persona.IconComponent;
            
            return (
              <div 
                key={index}
                className={`bg-white rounded-xl p-8 shadow-lg border-t-4 ${colors.border} hover:shadow-2xl transition-all duration-300 hover:-translate-y-1`}
              >
                <div className="flex flex-col items-center mb-6">
                  {/* Person Icon Component */}
                  <IconComponent size="large" showShoulders={true} className="mb-4" />
                  <h3 className={`text-3xl font-bold ${colors.text} mb-3 mt-2`}>
                    {persona.title}
                  </h3>
                  <div className="text-base text-gray-600 text-center leading-relaxed">
                    {persona.roles.map((role, i) => (
                      <React.Fragment key={i}>
                        {role}
                        {i < persona.roles.length - 1 && <br />}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
                <div className={`${colors.bg} rounded-lg p-6`}>
                  <p className={`text-lg font-semibold ${colors.text} mb-4`}>
                    Key Activities:
                  </p>
                  <ul className="text-base text-gray-700 space-y-3">
                    {persona.activities.map((activity, i) => (
                      <li key={i} className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>{activity}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-5 text-white text-center">
          <p className="text-xl font-medium">Unified Platform • Seamless Collaboration • Real-time Visibility</p>
        </div>
      </div>
    </SlideTemplate>
  );
};

export default PersonasSlide;