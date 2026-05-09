import sys

content = '''import React, { useState, useMemo, useEffect } from 'react';
import { Users, Calendar, ChevronDown, UserCog, Factory, Plus, Trash2, Check, X, Settings2, LayoutGrid, Globe } from 'lucide-react';
import { SuiviData, PlanningEvent, AppSettings } from '../types';

export interface EffectifsPageProps {
  onOpenGestionRH?: () => void;
  suivis?: SuiviData[];
  setSuivis?: React.Dispatch<React.SetStateAction<SuiviData[]>>;
  planningEvents?: PlanningEvent[];
  settings?: AppSettings;
}

type RoleCategory = 'Les chaines' | 'Responsables & Encadrement' | 'Finition' | 'L\\'emballage' | string;
type DisplayBy = 'CHAINES' | 'SALLES' | 'GLOBAL';

interface RoleDefinition {
  id: string;
  label: string;
  category: RoleCategory;
  isCustom?: boolean;
}

interface Salle {
  id: string;
  name: string;
}

const DEFAULT_ROLES: RoleDefinition[] = [
  { id: 'recta', label: 'Machinistes', category: 'Les chaines' },
  { id: 'sujet', label: 'Surjeteuses', category: 'Les chaines' },
  { id: 'sp', label: 'Spéciales', category: 'Les chaines' },
  { id: 'man', label: 'Manutention', category: 'Les chaines' },
  { id: 'chaf', label: 'Chef de chaine', category: 'Responsables & Encadrement' },
  { id: 'methodes', label: 'Méthodes', category: 'Responsables & Encadrement' },
  { id: 'qualite', label: 'Responsable Qualité', category: 'Responsables & Encadrement' },
  { id: 'mecanicien', label: 'Mécanicien', category: 'Responsables & Encadrement' },
  { id: 'finition', label: 'Opérateurs (Finition)', category: 'Finition' },
  { id: 'controle', label: 'Contrôle (Finition)', category: 'Finition' },
  { id: 'transp', label: 'Plieurs / Emballeurs', category: 'L\\'emballage' },
  { id: 'stager', label: 'Manutention (Emballage)', category: 'L\\'emballage' }
];

const DEFAULT_CATEGORY_CONFIG: Record<string, DisplayBy> = {
  'Les chaines': 'CHAINES',
  'Responsables & Encadrement': 'CHAINES',
  'Finition': 'SALLES',
  'L\\'emballage': 'SALLES'
};

export default function Effectifs({ onOpenGestionRH, suivis = [], setSuivis, planningEvents = [], settings }: EffectifsPageProps) {
  const [selectedChain, setSelectedChain] = useState('Toutes les chaines');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  
  // Custom roles state
  const [roles, setRoles] = useState<RoleDefinition[]>(() => {
    try {
      const saved = localStorage.getItem('BERA_CUSTOM_ROLES');
      return saved ? JSON.parse(saved) : DEFAULT_ROLES;
    } catch {
      return DEFAULT_ROLES;
    }
  });

  const [salles, setSalles] = useState<Salle[]>(() => {
    try {
      const saved = localStorage.getItem('BERA_SALLES');
      return saved ? JSON.parse(saved) : [{ id: 'salle_1', name: 'Salle 1' }];
    } catch { return [{ id: 'salle_1', name: 'Salle 1' }]; }
  });

  const [categoryConfigs, setCategoryConfigs] = useState<Record<string, DisplayBy>>(() => {
    try {
      const saved = localStorage.getItem('BERA_CATEGORY_CONFIGS');
      return saved ? JSON.parse(saved) : DEFAULT_CATEGORY_CONFIG;
    } catch { return DEFAULT_CATEGORY_CONFIG; }
  });

  useEffect(() => { localStorage.setItem('BERA_CUSTOM_ROLES', JSON.stringify(roles)); }, [roles]);
  useEffect(() => { localStorage.setItem('BERA_SALLES', JSON.stringify(salles)); }, [salles]);
  useEffect(() => { localStorage.setItem('BERA_CATEGORY_CONFIGS', JSON.stringify(categoryConfigs)); }, [categoryConfigs]);

  const [isAddingRole, setIsAddingRole] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [newRole, setNewRole] = useState({ label: '', category: 'Les chaines' });
  const [newCategory, setNewCategory] = useState('');
  const [newSalleName, setNewSalleName] = useState('');

  const activeSuivisForDate = useMemo(() => {
    return suivis.filter(s => s.date === selectedDate);
  }, [suivis, selectedDate]);

  const allKnownChains = useMemo(() => {
    const chains = new Set<string>();
    planningEvents.forEach(p => p.chaineId && chains.add(p.chaineId));
    suivis.forEach(s => s.chaineId && chains.add(s.chaineId) && !s.chaineId.startsWith('salle_') && s.chaineId !== 'global');
    if (settings?.chainsCount) {
      for (let i = 1; i <= settings.chainsCount; i++) {
        chains.add(\CHAINE \\);
      }
    }
    const result = Array.from(chains).sort();
    return result.length > 0 ? result : ['CHAINE 1']; // Fallback
  }, [planningEvents, suivis, settings]);

  const displayChains = useMemo(() => {
    if (selectedChain === 'Toutes les chaines') return allKnownChains;
    return allKnownChains.includes(selectedChain) ? [selectedChain] : [];
  }, [allKnownChains, selectedChain]);

  const getChainLabel = (chainId: string) => {
    return settings?.chainNames?.[chainId] || chainId;
  };

  const getEffectifValue = (targetId: string, roleId: string, type: 'chain'|'salle'|'global') => {
    let s;
    if (type === 'chain') {
      s = activeSuivisForDate.find(s => {
        const plan = planningEvents.find(p => p.id === s.planningId);
        return (plan?.chaineId || s.chaineId) === targetId;
      });
    } else {
      s = activeSuivisForDate.find(s => s.chaineId === targetId);
    }
    
    if (!s) return 0;
    if (roleId in s) return (s as any)[roleId] || 0;
    return s.customEffectifs?.[roleId] || 0;
  };

  const handleUpdate = (targetId: string, roleId: string, value: number, type: 'chain'|'salle'|'global') => {
    if (!setSuivis) return;
    setSuivis(prev => {
      const existingIndex = prev.findIndex(s => {
        if (s.date !== selectedDate) return false;
        if (type === 'chain') {
          const plan = planningEvents.find(p => p.id === s.planningId);
          return (plan?.chaineId || s.chaineId) === targetId;
        }
        return s.chaineId === targetId;
      });

      let updatedArray = [...prev];
      let s: SuiviData;

      if (existingIndex >= 0) {
        s = { ...updatedArray[existingIndex] };
      } else {
        s = {
          id: \effectif_\_\\,
          planningId: type === 'chain' ? '' : 'standalone',
          chaineId: targetId,
          date: selectedDate,
          entrer: 0,
          sorties: {},
          totalHeure: 0,
          pJournaliere: 0,
          enCour: 0,
          resteEntrer: 0,
          resteSortie: 0,
          totalWorkers: 0,
          customEffectifs: {}
        };
      }

      const isBuiltIn = DEFAULT_ROLES.some(r => r.id === roleId);
      if (isBuiltIn || roleId in s) {
        (s as any)[roleId] = value;
      } else {
        s.customEffectifs = { ...s.customEffectifs, [roleId]: value };
      }

      let total = 0;
      roles.forEach(r => {
        const val = DEFAULT_ROLES.some(dr => dr.id === r.id) || r.id in s 
          ? (s as any)[r.id] 
          : s.customEffectifs?.[r.id];
        total += Number(val) || 0;
      });
      s.totalWorkers = total;

      if (existingIndex >= 0) {
        updatedArray[existingIndex] = s;
      } else {
        updatedArray.push(s);
      }
      return updatedArray;
    });
  };

  const getColumnsForCategory = (category: string) => {
    const displayBy = categoryConfigs[category] || 'CHAINES';
    if (displayBy === 'SALLES') {
      return salles.map(s => ({ id: \salle_\\, label: s.name, type: 'salle' as const }));
    }
    if (displayBy === 'GLOBAL') {
      return [{ id: 'global', label: 'Global', type: 'global' as const }];
    }
    return displayChains.map(c => ({ id: c, label: getChainLabel(c), type: 'chain' as const }));
  };

  const calculateTotalForRow = (roleId: string, category: string) => {
    const cols = getColumnsForCategory(category);
    return cols.reduce((sum, col) => sum + parseInt(getEffectifValue(col.id, roleId, col.type) as string || '0'), 0);
  };

  const calculateTotalForCol = (colId: string, colType: 'chain'|'salle'|'global', category: string) => {
    const catRoles = roles.filter(r => r.category === category);
    return catRoles.reduce((sum, role) => sum + parseInt(getEffectifValue(colId, role.id, colType) as string || '0'), 0);
  };

  const rolesByCategory = useMemo(() => {
    const grouped: Record<string, RoleDefinition[]> = {};
    roles.forEach(r => {
      if (!grouped[r.category]) grouped[r.category] = [];
      grouped[r.category].push(r);
    });
    return grouped;
  }, [roles]);

  const handleAddRole = () => {
    if (!newRole.label) return;
    const cat = newCategory.trim() || newRole.category;
    setRoles([...roles, {
      id: \custom_\\,
      label: newRole.label,
      category: cat,
      isCustom: true
    }]);
    
    if (newCategory.trim() && !categoryConfigs[newCategory.trim()]) {
      setCategoryConfigs(prev => ({ ...prev, [newCategory.trim()]: 'CHAINES' }));
    }

    setNewRole({ label: '', category: 'Les chaines' });
    setNewCategory('');
    setIsAddingRole(false);
  };

  const handleDeleteRole = (id: string) => {
    if (confirm('Voulez-vous vraiment supprimer ce rôle ?')) {
      setRoles(roles.filter(r => r.id !== id));
    }
  };

  const handleRenameRole = (id: string, newLabel: string) => {
    setRoles(roles.map(r => r.id === id ? { ...r, label: newLabel } : r));
  };

  const handleAddSalle = () => {
    if (!newSalleName.trim()) return;
    setSalles([...salles, { id: \\\, name: newSalleName.trim() }]);
    setNewSalleName('');
  };

  const handleDeleteSalle = (id: string) => {
    if (confirm('Voulez-vous supprimer cette salle ?')) {
      setSalles(salles.filter(s => s.id !== id));
    }
  };

  const updateCategoryConfig = (category: string, displayBy: DisplayBy) => {
    setCategoryConfigs(prev => ({ ...prev, [category]: displayBy }));
  };

  return (
    <div className="flex-1 min-h-0 w-full overflow-y-auto bg-gradient-to-b from-slate-50 via-[#fafafa] to-slate-100">
      <div className="w-full max-w-full mx-auto box-border px-4 py-6 sm:px-6 flex flex-col gap-8">
        
        {/* HEADER & FILTERS */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-100 text-indigo-600 rounded-xl shadow-sm">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-slate-800 tracking-tight">Effectifs</h1>
              <p className="text-sm text-slate-500 font-medium">Répartition du personnel par chaîne, salle et date</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {onOpenGestionRH && (
              <button
                type="button"
                onClick={onOpenGestionRH}
                aria-label="Gestion RH détaillée"
                className="px-4 py-2 bg-sky-50 text-sky-600 hover:bg-sky-100 font-bold rounded-xl flex items-center gap-2 transition-colors shadow-sm"
              >
                <UserCog className="w-4 h-4" />
                <span className="hidden sm:inline">Gestion RH Détaillée</span>
              </button>
            )}

            <div className="relative">
              <select
                value={selectedChain}
                onChange={(e) => setSelectedChain(e.target.value)}
                className="appearance-none pl-4 pr-10 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              >
                <option value="Toutes les chaines">Toutes les chaines</option>
                {allKnownChains.map(c => <option key={c} value={c}>{getChainLabel(c)}</option>)}
              </select>
              <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Calendar className="h-4 w-4 text-slate-400" />
              </div>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              />
            </div>
          </div>
        </div>

        {/* ACTION BAR */}
        <div className="flex justify-end gap-3 w-full">
            <button
              onClick={() => setIsEditMode(!isEditMode)}
              className={\px-4 py-2 font-bold rounded-xl text-sm flex items-center gap-2 transition-colors \\}
            >
              <Settings2 className="w-4 h-4" />
              {isEditMode ? 'Terminer la configuration' : 'Configurer les Rôles / Salles'}
            </button>
            <button
              onClick={() => setIsAddingRole(!isAddingRole)}
              className="px-4 py-2 bg-indigo-600 text-white hover:bg-indigo-700 font-bold rounded-xl text-sm flex items-center gap-2 transition-colors shadow-sm"
            >
              {isAddingRole ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
              {isAddingRole ? 'Fermer' : 'Nouveau Rôle'}
            </button>
        </div>

        {/* EDIT CONFIG PANEL */}
        {isEditMode && (
          <div className="bg-amber-50/50 border border-amber-200 rounded-2xl p-5 shadow-sm mb-2 flex flex-col gap-6">
            <div>
              <h3 className="font-bold text-amber-900 mb-3 flex items-center gap-2"><LayoutGrid className="w-4 h-4"/> Gestion des Salles</h3>
              <div className="flex flex-wrap gap-3 items-center">
                {salles.map(s => (
                  <div key={s.id} className="bg-white border border-amber-200 px-3 py-1.5 rounded-lg text-sm font-bold text-amber-800 flex items-center gap-2 shadow-sm">
                    {s.name}
                    <button onClick={() => handleDeleteSalle(s.id)} className="text-amber-400 hover:text-red-500 transition-colors">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
                <div className="flex items-center gap-2 ml-2">
                  <input 
                    type="text" 
                    value={newSalleName} 
                    onChange={e => setNewSalleName(e.target.value)}
                    placeholder="Nom de la salle..."
                    className="px-3 py-1.5 rounded-lg border border-amber-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                    onKeyDown={e => e.key === 'Enter' && handleAddSalle()}
                  />
                  <button onClick={handleAddSalle} disabled={!newSalleName.trim()} className="p-1.5 bg-amber-200 text-amber-800 rounded-lg hover:bg-amber-300 disabled:opacity-50">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="text-sm text-amber-800 bg-amber-100/50 p-3 rounded-xl border border-amber-200/50">
              <p className="font-semibold mb-1">Comment ça marche ?</p>
              <ul className="list-disc list-inside space-y-1 opacity-90">
                <li><strong>Par Chaine:</strong> Colonnes = Chaines actives f la date séléctionnée.</li>
                <li><strong>Par Salle:</strong> Colonnes = Salles (idkhel numéro wa7d par salle, mzyana l'Emballage/Finition).</li>
                <li><strong>Globale:</strong> Colonne wa7da "Global" l'usine kaml.</li>
              </ul>
            </div>
          </div>
        )}

        {isAddingRole && (
          <div className="px-5 py-4 bg-indigo-50/50 border border-indigo-100 rounded-2xl flex flex-wrap items-end gap-4 shadow-sm mb-4">
            <div>
              <label className="block text-xs font-bold text-indigo-800 mb-1">Catégorie</label>
              <div className="flex gap-2">
                <select 
                  value={newRole.category}
                  onChange={e => { setNewRole({...newRole, category: e.target.value}); setNewCategory(''); }}
                  className="pl-3 pr-8 py-2 border border-indigo-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  {Object.keys(rolesByCategory).map(cat => <option key={cat} value={cat}>{cat}</option>)}
                  <option value="NEW">+ Nouvelle Catégorie</option>
                </select>
                {newRole.category === 'NEW' && (
                  <input 
                    type="text" 
                    placeholder="Nom de la catégorie"
                    value={newCategory}
                    onChange={e => setNewCategory(e.target.value)}
                    className="px-3 py-2 border border-indigo-200 rounded-lg text-sm w-48 focus:ring-2 focus:ring-indigo-500 bg-white"
                  />
                )}
              </div>
            </div>
            <div>
              <label className="block text-xs font-bold text-indigo-800 mb-1">Nom du Rôle / Poste</label>
              <input 
                type="text" 
                placeholder="Ex: Machine Laser, Coupe..."
                value={newRole.label}
                onChange={e => setNewRole({...newRole, label: e.target.value})}
                className="px-3 py-2 border border-indigo-200 rounded-lg text-sm w-64 focus:ring-2 focus:ring-indigo-500 bg-white"
                onKeyDown={e => e.key === 'Enter' && handleAddRole()}
              />
            </div>
            <button 
              onClick={handleAddRole}
              disabled={!newRole.label || (newRole.category === 'NEW' && !newCategory)}
              className="px-4 py-2 bg-indigo-600 text-white font-bold rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              <Check className="w-4 h-4" /> Ajouter
            </button>
          </div>
        )}

        {/* CATEGORY TABLES */}
        {Object.entries(rolesByCategory).map(([category, catRoles]) => {
          const cols = getColumnsForCategory(category);
          const currentConfig = categoryConfigs[category] || 'CHAINES';
          
          return (
            <div key={category} className="bg-white border border-slate-200 shadow-sm rounded-2xl flex flex-col w-full overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50 flex flex-wrap gap-4 justify-between items-center">
                <div className="flex items-center gap-2">
                  {currentConfig === 'SALLES' ? <LayoutGrid className="w-5 h-5 text-indigo-500" /> : 
                   currentConfig === 'GLOBAL' ? <Globe className="w-5 h-5 text-indigo-500" /> :
                   <Factory className="w-5 h-5 text-indigo-500" />}
                  <h2 className="text-lg font-bold text-slate-800">{category}</h2>
                </div>
                {isEditMode && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Répartition:</span>
                    <select 
                      value={currentConfig}
                      onChange={e => updateCategoryConfig(category, e.target.value as DisplayBy)}
                      className="text-sm font-bold text-slate-700 bg-white border border-slate-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-indigo-500 outline-none"
                    >
                      <option value="CHAINES">Par Chaine</option>
                      <option value="SALLES">Par Salle</option>
                      <option value="GLOBAL">Globale</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="px-4 py-3 font-semibold text-slate-600 w-64 min-w-[16rem] sticky left-0 bg-slate-50 shadow-[1px_0_0_0_#e2e8f0] z-10">
                        Rôle / {currentConfig === 'SALLES' ? 'Salle' : currentConfig === 'GLOBAL' ? 'Global' : 'Chaine'}
                      </th>
                      {cols.map(c => (
                        <th key={c.id} className="px-4 py-3 font-bold text-slate-800 text-center min-w-[6rem]">
                          <div className="flex flex-col items-center">
                            <span>{c.label}</span>
                            <span className="text-xs font-medium text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-full mt-1">
                              Total: {calculateTotalForCol(c.id, c.type, category)}
                            </span>
                          </div>
                        </th>
                      ))}
                      <th className="px-4 py-3 font-bold text-slate-800 text-center bg-slate-100/50 min-w-[5rem]">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {catRoles.map(row => (
                      <tr key={row.id} className="hover:bg-slate-50/50 transition-colors group">
                        <td className="px-4 py-3 font-medium text-slate-700 bg-white group-hover:bg-slate-50/50 sticky left-0 shadow-[1px_0_0_0_#e2e8f0] z-10 flex items-center justify-between">
                          {isEditMode ? (
                            <input 
                              type="text" 
                              value={row.label}
                              onChange={(e) => handleRenameRole(row.id, e.target.value)}
                              className="w-full bg-amber-50 border border-amber-200 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-amber-500 mr-2"
                            />
                          ) : (
                            <span>{row.label}</span>
                          )}
                          
                          {isEditMode && (
                            <button 
                              onClick={() => handleDeleteRole(row.id)}
                              className="text-slate-400 hover:text-red-500 transition-colors p-1.5 rounded hover:bg-red-50 flex-shrink-0"
                              title="Supprimer ce rôle"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </td>
                        {cols.map(c => {
                          const val = getEffectifValue(c.id, row.id, c.type);
                          return (
                            <td key={\\-\\} className="px-2 py-2 text-center">
                              <input
                                type="number"
                                min="0"
                                value={val === 0 ? '' : val}
                                onChange={(e) => handleUpdate(c.id, row.id, parseInt(e.target.value) || 0, c.type)}
                                className="w-16 text-center font-bold text-indigo-700 border-b-2 border-slate-200 hover:border-indigo-300 focus:border-indigo-500 focus:outline-none bg-transparent transition-colors"
                                placeholder="0"
                              />
                            </td>
                          );
                        })}
                        <td className="px-4 py-3 text-center font-black text-indigo-600 bg-slate-100/50">
                          {calculateTotalForRow(row.id, category)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}

      </div>
    </div>
  );
}
'''

with open('Effectifs.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
